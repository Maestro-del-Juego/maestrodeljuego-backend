from rest_framework import serializers
from .models import Game, CustomUser, Tag, GameNight, Contact, Voting, GeneralFeedback, GameFeedback, RSVP
from djoser.serializers import UserCreatePasswordRetypeSerializer
from drf_writable_nested import WritableNestedModelSerializer
from django.db.models.query import QuerySet
from calendar import day_name
from datetime import date


class GameListSerializer(serializers.ModelSerializer):
    categories = serializers.StringRelatedField(many=True)

    class Meta:
        model = Game
        fields = (
            'pk',
            'bgg',
            'title',
            'pub_year',
            'image',
            'playtime',
            'min_players',
            'max_players',
            'categories',
        )


class UserNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            'pk',
            'username',
            'avatar',
        )


class GameDetailSerializer(serializers.ModelSerializer):
    owned = serializers.SerializerMethodField()
    wishlisted = serializers.SerializerMethodField()
    categories = serializers.StringRelatedField(many=True)

    class Meta:
        model = Game
        fields = (
            'title',
            'bgg',
            'pub_year',
            'description',
            'min_players',
            'max_players',
            'image',
            'playtime',
            'player_age',
            'categories',
            'owned',
            'wishlisted'
        )

    def get_owned(self, obj):
        user = self.context['request'].user
        owners = obj.owners.all()
        if user in owners:
            return True
        return False

    def get_wishlisted(self, obj):
        user = self.context['request'].user
        wishers = obj.wishlisted.all()
        if user in wishers:
            return True
        return False


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = (
            'pk',
            'first_name',
            'last_name',
            'email'
        )


class RSVPSerializer(serializers.ModelSerializer):
    gamenight = serializers.StringRelatedField()
    invitee = ContactSerializer(read_only=True)
    class Meta:
        model = RSVP
        fields = (
            'pk',
            'gamenight',
            'invitee',
            'attending',
        )


class RSVPForGameNightSerializer(serializers.ModelSerializer):
    invitee = serializers.StringRelatedField()
    class Meta:
        model = RSVP
        fields = (
            'invitee',
            'attending'
        )


class GameForGameNightSerializer(serializers.ModelSerializer):
    votes = serializers.SerializerMethodField()
    # feedback = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = (
            'pk',
            'bgg',
            'title',
            'pub_year',
            'image',
            'votes',
            # 'feedback',
        )

    def get_votes(self, obj):
        serialized_instance = self.parent.parent.instance
        if isinstance(serialized_instance, QuerySet):
            return None
        gamenight = serialized_instance
        votes = obj.tally_votes(gamenight)
        return votes

    # def get_feedback(self, obj):
    #     serialized_instance = self.parent.parent.instance
    #     if isinstance(serialized_instance, QuerySet):
    #         return None
    #     gamenight = serialized_instance
    #     feedback = 
    #     rating = obj.calc_feedback(gamenight)
    #     return rating


class GameNightSerializer(serializers.ModelSerializer):
    user = UserNestedSerializer(read_only=True)
    invitees = ContactSerializer(many=True)
    rsvps = RSVPForGameNightSerializer(many=True)
    attendees = ContactSerializer(many=True)
    games = GameListSerializer(read_only=True, many=True)
    options = GameForGameNightSerializer(read_only=True, many=True)
    # feedback = serializers.SerializerMethodField()

    class Meta:
        model = GameNight
        fields = (
            'pk',
            'rid',
            'user',
            'date',
            'status',
            'invitees',
            'rsvps',
            'attendees',
            'games',
            'start_time',
            'end_time',
            'location',
            'options',
            # 'feedback',
        )

    # def get_feedback(self, obj):
    #     return obj.calc_feedback()


class GameNightCreateSerializer(serializers.ModelSerializer):
    user = UserNestedSerializer(read_only=True)

    class Meta:
        model = GameNight
        fields = (
            'pk',
            'rid',
            'user',
            'date',
            'status',
            'invitees',
            'games',
            'start_time',
            'end_time',
            'location',
            'options'
        )


class DjoserUserSerializer(serializers.ModelSerializer):
    games = GameListSerializer(many=True, read_only=True)
    wishlist = GameListSerializer(many=True, read_only=True)
    contacts = ContactSerializer(many=True, read_only=True)
    gamenights = GameNightSerializer(many=True, read_only=True)
    weekday_stats = serializers.SerializerMethodField()
    most_common_players = serializers.SerializerMethodField()
    most_played_games = serializers.SerializerMethodField()
    class Meta:
        model = CustomUser
        fields = (
            'pk',
            'username',
            'email',
            'avatar',
            'games',
            'wishlist',
            'contacts',
            'gamenights',
            'weekday_stats',
            'most_common_players',
            'most_played_games',
        )

    # methods for weekday_stats field
    def get_weekday_stats(self, obj):
        user = obj
        gamenight_dict = self.build_week_dict(user)
        days = gamenight_dict.keys()
        stats_dict = {
            'avg_overall_feedback': {},
            'avg_attend_ratio': {},
            'avg_session_len': {},
            'avg_game_num': {},
            'avg_player_num': {},
            'sessions_num': {}
        }
        for day in days:
            gamenights = gamenight_dict[day]
            stats_dict['avg_overall_feedback'][day] = self.days_avg_overall(gamenights)
            stats_dict['avg_attend_ratio'][day] = self.days_avg_attend(gamenights)
            stats_dict['avg_session_len'][day] = self.days_avg_session_len(gamenights)
            stats_dict['avg_game_num'][day] = self.days_avg_game_num(gamenights)
            stats_dict['avg_player_num'][day] = self.days_avg_player_num(gamenights)
            stats_dict['sessions_num'][day] = len(gamenights)
        return stats_dict

    def build_week_dict(self, user):
        '''
        Builds a dictionary where the keys are the names for the days of the
        week and the values are the GameNights that occurred on that day.
        '''
        gamenights = user.gamenights.filter(status="Finalized")
        game_days = {}
        days = list(day_name)
        for day in days:
            game_days[day] = []
        for night in gamenights:
            day = night.date.weekday()
            game_days[days[day]].append(night)
        return game_days

    def days_avg_overall(self, gamenights):
        '''
        Takes a list of GameNight objects and returns the average overall
        rating among them.
        '''
        gamenight_num = len(gamenights)
        total = 0
        for gamenight in gamenights:
            overall = gamenight.calc_avg_overall()
            if overall == None:
                gamenight_num -= 1
                continue
            total += overall
        if gamenight_num == 0:
            average = None
        else:
            average = round(total/gamenight_num, 2)
        return average

    def days_avg_attend(self, gamenights):
        '''
        Takes a list of GameNight objects and returns the average attendance
        ratio among them.
        '''
        gamenight_num = len(gamenights)
        total = 0
        for gamenight in gamenights:
            attendees_num = len(gamenight.attendees.all())
            invitees_num = len(gamenight.invitees.all())
            if invitees_num == None:
                gamenight_num -= 1
                continue
            attendance = round(attendees_num/invitees_num, 2)
            total += attendance
        if gamenight_num == 0:
            average = None
        else:
            average = round(total/gamenight_num, 2)
        return average

    def days_avg_session_len(self, gamenights):
        '''
        Takes a list of GameNight objects and returns the average session
        length (in minutes) among them.
        '''
        gamenight_num = len(gamenights)
        total = 0
        for gamenight in gamenights:
            session_len = gamenight.calc_session_len()
            if session_len == None:
                gamenight_num -= 1
                continue
            total += session_len
        if gamenight_num == 0:
            average = None
        else:
            average = round(total/gamenight_num, 2)
        return average

    def days_avg_game_num(self, gamenights):
        '''
        Takes a list of GameNight objects and returns the average number of
        unique games played among them.
        '''
        gamenight_num = len(gamenights)
        total = 0
        for gamenight in gamenights:
            game_num = len(gamenight.games.all())
            if game_num == 0:
                gamenight_num -=1
                continue
            total += game_num
        if gamenight_num == 0:
            average = None
        else:
            average = round(total/gamenight_num, 2)
        return average

    def days_avg_player_num(self, gamenights):
        '''
        Takes a list of GameNight objects and returns the average number of
        players among them.
        '''
        gamenight_num = len(gamenights)
        total = 0
        for gamenight in gamenights:
            player_num = len(gamenight.attendees.all())
            if player_num ==0:
                gamenight_num -=1
                continue
            total += player_num
        if gamenight_num == 0:
            average = None
        else:
            average = round(total/gamenight_num, 2)
        return average

    def get_most_common_players(self, obj):
        contacts = obj.contacts.all()
        return_list = []
        name_pk_dict = {}
        freq_dict = {}
        for contact in contacts:
            gamenights = len(contact.attended.all())
            freq_dict[str(contact)] = gamenights
            name_pk_dict[str(contact)] = contact.pk
        contacts_sort = sorted(freq_dict, key=freq_dict.__getitem__)
        if len(contacts) < 5:
            index = -1
            max = -len(contacts) - 1
            while index > max:
                name = contacts_sort[index]
                pk = name_pk_dict[name]
                return_list.append({'name': name, 'pk': pk, 'attended': freq_dict[name]})
                index -= 1
        else:
            index = -1
            while index > -6:
                name = contacts_sort[index]
                pk = name_pk_dict[name]
                return_list.append({'name': name, 'pk': pk, 'attended': freq_dict[name]})
                index -= 1
        return return_list

    def get_most_played_games(self, obj):
        games = obj.games.all()
        return_list = []
        other_data_dict = {}
        freq_dict = {}
        for game in games:
            gamenights = len(game.gamenights.all())
            freq_dict[str(game)] = gamenights
            other_data_dict[str(game)] = {'bgg': game.bgg, 'pub_year': game.pub_year, 'image': game.image}
        games_sort = sorted(freq_dict, key=freq_dict.__getitem__)
        breakpoint()
        if len(games) < 5:
            index = -1
            max = -len(games) - 1
            while index > max:
                name = games_sort[index]
                other_data = other_data_dict[name]
                return_list.append({'name': name, 'bgg': other_data['bgg'], 'pub_year': other_data['pub_year'], 'image': other_data['image'], 'played': freq_dict[name]})
                index -= 1
        else:
            index = -1
            while index > -6:
                name = games_sort[index]
                other_data = other_data_dict[name]
                return_list.append({'name': name, 'bgg': other_data['bgg'], 'pub_year': other_data['pub_year'], 'image': other_data['image'], 'played': freq_dict[name]})
                index -= 1
        return return_list



class DjoserRegistrationSerializer(UserCreatePasswordRetypeSerializer):
    class Meta(UserCreatePasswordRetypeSerializer.Meta):
        fields = (
            'username',
            'avatar',
            'email',
            'password',
        )


class TagListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'name',
            'user',
        )
        


class GameFeedbackSerializer(serializers.ModelSerializer):

    class Meta:
        model = GameFeedback
        fields = (
            'gamenight',
            'attendee',
            'game',
            'rating',
        )


class GeneralFeedbackSerializer(serializers.ModelSerializer):

    class Meta:
        model = GeneralFeedback
        fields = (
            'gamenight',
            'attendee',
            'overall_rating',
            'people_rating',
            'location_rating',
            'comments',
        )


class VotingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voting
        fields = (
            'gamenight',
            'invitee',
            'game',
            'vote'
        )
