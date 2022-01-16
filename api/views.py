from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView
from .models import Game
from .serializers import GameListSerializer, GameDetailSerializer
import requests, json, xmltodict, decimal


class LibraryView(ListAPIView):
    serializer_class = GameListSerializer

    def get_queryset(self):
        queryset = Game.objects.filter(user_id=self.request.user.pk)
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

        obj = self.get_game(queryset, **filter_kwargs)

        self.check_object_permissions(self.request, obj)

        return obj


def new_game(bgg):
    url = f"https://www.boardgamegeek.com/xmlapi2/thing?id={bgg}&stats=1"
    response = requests.get(url)
    ordered_dict = xmltodict.parse(response.text)
    game_dict_nest = json.loads(json.dumps(ordered_dict))
    game_dict = game_dict_nest['items']['item']

    game_obj = create_game_obj(game_dict)

    game_obj.save()

    return game_obj

def get_primary_name(names_list):
    for name in names_list:
        if name['@type'] == 'primary':
            return name['@value']

def create_game_obj(game_dict):
    names = game_dict['name']

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

    return game_obj








class WishListView(ListAPIView):
    serializer_class = GameListSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = user.wishlist.all()
        return queryset