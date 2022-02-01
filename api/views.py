from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.core.exceptions import BadRequest
from rest_framework.generics import ListAPIView, RetrieveUpdateAPIView, ListCreateAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from .models import Game, GameNight, Tag, Category, Contact, Voting, GeneralFeedback, GameFeedback, RSVP
from .serializers import GameListSerializer, GameNightSerializer, GameDetailSerializer, TagListSerializer, ContactSerializer, VotingSerializer, GameNightCreateSerializer, GeneralFeedbackSerializer, GameFeedbackSerializer, RSVPSerializer
from .permissions import IsAuthorOrReadOnly
import requests, json, xmltodict, decimal, string, random
from datetime import date, datetime, timedelta
from rest_framework import status
from rest_framework.response import Response
from .tasks import test_email
from celery.app.control import Control
from celery.result import AsyncResult
from api import serializers


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
    # queryset = GameNight.objects.all()
    serializer_class = GameNightSerializer
    # permission_classes = [IsAuthorOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        queryset = user.gamenights.all()
        return queryset

    def perform_create(self, serializer):
        rand_id = self.get_rid()
        serializer.save(user=self.request.user, rid=rand_id)
        gamenight = GameNight.objects.get(rid=rand_id)
        gamenight.mail_gamenight_create()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return GameNightCreateSerializer
        return super().get_serializer_class()

    def get_rid(self):
        '''
        randomly generates 15-character long string
        '''
        rid = ''.join(random.choices(string.ascii_letters+string.digits, k=15))
        while GameNight.objects.filter(rid=rid).exists():
            rid = ''.join(random.choices(string.ascii_letters+string.digits, k=15))
        return rid


class TagListView(ListCreateAPIView):
    serializer_class = TagListSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Tag.objects.filter(user_id=user.id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GameNightDetailView(RetrieveUpdateAPIView):
    queryset = GameNight.objects.all()
    serializer_class = GameNightSerializer
    permission_classes = [IsAuthorOrReadOnly]

    # def get_queryset(self):
    #     user = self.request.user
    #     queryset = user.gamenights.all()
    #     return queryset


    def get_object(self):
        '''
        overridden to grab GameNight object based on rid in the URL
        '''
        gamenight_rid = self.kwargs['rid']
        queryset = self.filter_queryset(self.get_queryset())
        obj = get_object_or_404(queryset, rid=gamenight_rid)
        self.check_object_permissions(self.request, obj)
        return obj

    def perform_update(self, serializer):
        gamenight = self.get_object()
        data = self.request.data

        if 'attendees' in data:
            contacts = data['attendees']
            for contact in contacts:
                pk = contact['pk']
                gamenight.update_attendees(pk)
                gamenight.save()
        elif 'invitees' in data:
            contacts = data['invitees']
            for contact in contacts:
                pk = contact['pk']
                gamenight.update_invitees(pk)
                gamenight.save()
        elif 'options' in data:
            games = data['options']
            for game in games:
                pk = game['pk']
                gamenight.update_options(pk)
                gamenight.save()
        elif 'games' in data:
            games = data['games']
            for game in games:
                pk = game['pk']
                gamenight.update_games(pk)
                gamenight.save()

        serializer.save()

        updated_gamenight = self.get_object()
        if 'status' in data:
            gn_status = gamenight.status
            if data['status'] == 'Finalized' or gn_status == 'Finalized':
                if data['status'] != gn_status:
                    updated_gamenight.update_feedback_task()
        if 'date' in data:
            if data['date'] != str(gamenight.date):
                updated_gamenight.update_feedback_task()



class ContactListView(ListCreateAPIView):
    serializer_class = ContactSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Contact.objects.filter(user_id=user.id)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class VotingView(CreateAPIView):
    serializer_class = VotingSerializer

    def get_queryset(self):
        gamenight_rid = self.kwargs['rid']
        gamenight = GameNight.objects.get(rid=gamenight_rid)
        queryset = gamenight.voting.all()
        return queryset

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        data = self.request.data
        data_copy = data.copy()
        gamenight = GameNight.objects.get(rid=self.kwargs['rid'])
        invitee = Contact.objects.get(pk=data[0]['invitee'])
        for vote in data_copy:
            game = Game.objects.get(pk=vote['game'])
            if Voting.objects.filter(gamenight=gamenight, invitee=invitee, game=game).exists():
                data_copy.remove(vote)
        kwargs['data'] = data_copy
        return serializer_class(*args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ContactUpdateView(RetrieveUpdateDestroyAPIView):
    serializer_class = ContactSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = Contact.objects.filter(user_id=user.id)
        return queryset


class GeneralFeedbackView(CreateAPIView):
    serializer_class = GeneralFeedbackSerializer

    def get_queryset(self):
        gamenight_rid = self.kwargs['rid']
        gamenight = GameNight.objects.get(rid=gamenight_rid)
        queryset = gamenight.generalfeedback.all()
        return queryset

    def perform_create(self, serializer):
        attendee_pk = self.request.data['attendee']
        contact = Contact.objects.get(pk=attendee_pk)
        gamenight = GameNight.objects.get(rid=self.kwargs['rid'])

        if not GeneralFeedback.objects.filter(gamenight=gamenight, attendee=contact).exists():
            serializer.save(gamenight=gamenight, attendee=contact)

            return True
        return False

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        saved = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        if saved:
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        not_saved = {'detail': 'Attendee has already left feedback.'}
        return Response(not_saved, status=status.HTTP_418_IM_A_TEAPOT, headers=headers)


class GameFeedbackView(CreateAPIView):
    serializer_class = GameFeedbackSerializer

    def get_queryset(self):
        gamenight_rid = self.kwargs['rid']
        gamenight = GameNight.objects.get(rid=gamenight_rid)
        queryset = gamenight.gamefeedback.all()
        return queryset

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        data = self.request.data
        data_copy = data.copy()
        gamenight = GameNight.objects.get(rid=self.kwargs['rid'])
        contact = Contact.objects.get(pk=data[0]['attendee'])
        for feedback in data_copy:
            game = Game.objects.get(pk=feedback['game'])
            if GameFeedback.objects.filter(gamenight=gamenight, attendee=contact, game=game).exists():
                data_copy.remove(feedback)
        kwargs['data'] = data_copy
        return serializer_class(*args, **kwargs)

    def perform_create(self, serializer):
        attendee_pk = self.request.data[0]['attendee']
        contact = Contact.objects.get(pk=attendee_pk)
        gamenight = GameNight.objects.get(rid=self.kwargs['rid'])
        if not GameFeedback.objects.filter(gamenight=gamenight, attendee=contact).exists():
            serializer.save(gamenight=gamenight, attendee=contact)
            return True
        return False

    def create(self, request, *args, **kwargs):
        if len(request.data) == 0:
            response = {'detail': 'Nothing to save here.'}
            return Response(response, status=status.HTTP_204_NO_CONTENT, headers=self.default_response_headers)
        serializer = self.get_serializer(data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        saved = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        if saved:
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        not_saved = {'detail': 'Attendee has already left feedback.'}
        return Response(not_saved, status=status.HTTP_418_IM_A_TEAPOT, headers=headers)


class RSVPListCreateView(ListCreateAPIView):
    serializer_class = RSVPSerializer

    def get_queryset(self):
        gamenight_rid = self.kwargs['rid']
        gamenight = GameNight.objects.get(rid=gamenight_rid)
        queryset = gamenight.rsvps.all()
        return queryset

    def perform_create(self, serializer):
        invitee = self.request.data['invitee']
        contact = Contact.objects.get(
            first_name=invitee['first_name'],
            last_name=invitee['last_name'],
            email=invitee['email'],
            user=self.request.user
        )
        gamenight = GameNight.objects.get(rid=self.kwargs['rid'])
        if not RSVP.objects.filter(gamenight=gamenight, invitee=contact).exists():
            serializer.save(gamenight=gamenight, invitee=contact)
            if self.request.data['attending'] == 'True':
                gamenight.update_attendees(contact.pk)
            return True
        return False

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        saved = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        if saved:
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        not_saved = {'detail': 'Invitee has already RSVPed.'}
        return Response(not_saved, status=status.HTTP_418_IM_A_TEAPOT, headers=headers)

