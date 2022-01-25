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


class UserStatsSerializer(serializers.Serializer):
    weekday_stats = serializers.SerializerMethodField()

    def build_week_dict(self):
        '''
        Builds a dictionary where the keys are the names for the days of the
        week and the values are the GameNights that occurred on that day.
        '''
        # this line will probably need bugfixing, but I think this is the solution
        user = self.parent.instance
        gamenights = user.gamenights.all()
        game_days = {}
        days = list(day_name)
        for day in days:
            game_days[day] = []
        for night in gamenights:
            day = night.date.weekday()
            game_days[days[day]].append(night)
        return game_days

    def get_weekday_stats(self):

        days_dict = self.build_week_dict()
        days = days_dict.keys()
        stats_dict = {
            'avg_overall_feedback': {},
            'avg_attend_ratio': {},
            'avg_session_len': {},
            'avg_game_num': {},
            'avg_player_num': {},
            'sessions_num': {}
        }
        for day in days:
            gamenights = days_dict[day]
            stats_dict['avg_overall_feedback'][day] = self.days_avg_overall(gamenights)
            stats_dict['avg_attend_ratio'][day] = self.days_avg_attend(gamenights)
            stats_dict['avg_session_length'][day] = self.days_avg_session_len(gamenights)
            stats_dict['avg_game_num'][day] = self.days_avg_game_num(gamenights)
            stats_dict['avg_player_num'][day] = self.days_avg_player_num(gamenights)
            stats_dict['sessions_num'][day] = self.days_sessions_num(gamenights)


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
        Takes a list of GameNight objects and returns the average attendence
        ratio among them.
        '''
        pass

    def days_avg_session_len(self, gamenights):
        '''
        Takes a list of GameNight objects and returns the average session
        length (in minutes) among them.
        '''
        pass

    def days_avg_game_num(self, gamenights):
        '''
        Takes a list of GameNight objects and returns the average number of
        unique games played among them.
        '''
        pass

    def days_avg_player_num(self, gamenights):
        '''
        Takes a list of GameNight objects and returns the average number of
        players among them.
        '''
        pass

    def days_sessions_num(self, gamenights):
        '''
        Takes a list of GameNight objects and returns the total number of
        game night sessions.
        '''
        pass







class DjoserUserSerializer(serializers.ModelSerializer):
    games = GameListSerializer(many=True, read_only=True)
    wishlist = GameListSerializer(many=True, read_only=True)
    contacts = ContactSerializer(many=True, read_only=True)
    gamenights = GameNightSerializer(many=True, read_only=True)
    statistics = UserStatsSerializer()
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
            'statistics',
        )


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
