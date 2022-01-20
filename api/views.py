from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView, ListCreateAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Game, GameNight, Tag, Category, Contact
from .serializers import GameListSerializer, GameNightSerializer, GameDetailSerializer, TagListSerializer, ContactListSerializer, VotingSerializer, GameNightCreateSerializer
import requests, json, xmltodict, decimal
from datetime import date


class LibraryView(ListAPIView):
    serializer_class = GameListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = user.games.all()
        return queryset


class GameDetailView(RetrieveUpdateAPIView):
    serializer_class = GameDetailSerializer
    queryset = Game.objects.all()
    lookup_field = 'bgg'

    def get_game(self, queryset, bgg):
        if queryset.filter(bgg=bgg).exists():
            return queryset.filter(bgg=bgg)[0]
        else:
            return new_game(bgg)

    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())

        lookup_url_kwarg = self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            'Expected view %s to be called with a URL keyword argument '
            'named "%s". Fix your URL conf, or set the `.lookup_field` '
            'attribute on the view correctly.' %
            (self.__class__.__name__, lookup_url_kwarg)
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}

        # This is the only line changed from the original method
        obj = self.get_game(queryset, **filter_kwargs)

        self.check_object_permissions(self.request, obj)

        return obj

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        data = self.request.data
        if 'owned' in data:
            kwargs['data'] = {}
        return serializer_class(*args, **kwargs)

    def perform_update(self, serializer):
        game = self.get_object()
        user = self.request.user
        data = self.request.data
        if 'owned' in data:
            game.update_owners(user)
        elif 'wishlisted' in data:
            game.update_wishlisted(user)
        game.save()


def new_game(bgg):
    '''
    Takes a BGG ID and returns the associated game object.
    '''

    url = f"https://www.boardgamegeek.com/xmlapi2/thing?id={bgg}&stats=1"

    game_dict = xml_to_dict(url)

    game_obj = create_game_obj(game_dict)

    return game_obj

def xml_to_dict(url):
    response = requests.get(url)
    ordered_dict = xmltodict.parse(response.text)
    game_dict_nest = json.loads(json.dumps(ordered_dict))
    game_dict = game_dict_nest['items']['item']
    return game_dict

def get_primary_name(names_list):
    '''
    Returns the English name of the specified board game
    '''

    if isinstance(names_list, dict):
        return names_list['@value']

    for name in names_list:
        if name['@type'] == 'primary':
            return name['@value']

def create_game_obj(game_dict):
    '''
    Creates an instance of the Game class using data from the given dictionary.
    '''

    names = game_dict['name']
    link_dict = game_dict['link']

    game_obj = Game(
        title=get_primary_name(names),
        bgg=int(game_dict['@id']),
        image=game_dict['image'],
        pub_year=int(game_dict['yearpublished']['@value']),
        min_players=int(game_dict['minplayers']['@value']),
        max_players=int(game_dict['maxplayers']['@value']),
        playtime=int(game_dict['playingtime']['@value']),
        player_age=int(game_dict['minage']['@value']),
        weight=decimal.Decimal(game_dict['statistics']['ratings']['averageweight']['@value'])
    )

    game_obj.save()

    game_obj.categories.set(get_categories(link_dict))

    return game_obj

def get_categories(link_dict):
    categories = []

    for item in link_dict:
        if item['@type'] == 'boardgamecategory':
            name = item['@value']
            category = Category.objects.get(name=name)
            categories.append(category)

    return categories


class WishListView(ListAPIView):
    serializer_class = GameListSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = user.wishlist.all()
        return queryset


class GameNightView(ListCreateAPIView):
    serializer_class = GameNightSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = GameNight.objects.filter(user_id=user.id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return GameNightCreateSerializer
        return super().get_serializer_class()


class TagListView(ListCreateAPIView):
    serializer_class = TagListSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Tag.objects.filter(user_id=user.id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GameNightDetailView(RetrieveUpdateAPIView):
    serializer_class = GameNightSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = user.gamenights.all()
        return queryset

    def get_object(self):
        gamenight_date = date(self.kwargs['year'], self.kwargs['month'], self.kwargs['day'])
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(queryset, date=gamenight_date)
        self.check_object_permissions(self.request, obj)
        return obj


class ContactListView(ListCreateAPIView):
    serializer_class = ContactListSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Contact.objects.filter(user_id=user.id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class VotingView(CreateAPIView):
    serializer_class = VotingSerializer

    def get_queryset(self):
        user = self.request.user
        gamenight_date = date(self.kwargs['year'], self.kwargs['month'], self.kwargs['day'])
        gamenight = GameNight.objects.get(date=gamenight_date, user=user)
        queryset = gamenight.voting.all()