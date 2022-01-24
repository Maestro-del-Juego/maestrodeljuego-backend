from rest_framework import serializers
from .models import Game, CustomUser, Tag, GameNight, Contact, Voting, GeneralFeedback, GameFeedback, RSVP
from djoser.serializers import UserCreatePasswordRetypeSerializer
from drf_writable_nested import WritableNestedModelSerializer, UniqueFieldsMixin, NestedCreateMixin
from django.db.models.query import QuerySet


class GameListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = (
            'pk',
            'bgg',
            'title',
            'pub_year',
            'image',
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
    attendees = ContactSerializer(many=True)
    games = GameListSerializer(read_only=True, many=True)
    options = GameForGameNightSerializer(read_only=True, many=True)
    feedback = serializers.SerializerMethodField()

    class Meta:
        model = GameNight
        fields = (
            'pk',
            'rid',
            'user',
            'date',
            'status',
            'invitees',
            'attendees',
            'games',
            'start_time',
            'end_time',
            'location',
            'options',
            'feedback',
        )

    def get_feedback(self, obj):
        return obj.calc_feedback()



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
        

class VotingSerializer(serializers.ModelSerializer):
    gamenight = serializers.StringRelatedField(read_only=True)
    invitee = ContactSerializer()
    class Meta:
        model = Voting
        fields = (
            'gamenight',
            'invitee',
            'game',
            'vote'
        )

class GameFeedbackSerializer(serializers.ModelSerializer):
    # gamenight = serializers.StringRelatedField(read_only=True)
    # attendee = ContactSerializer()

    class Meta:
        model = GameFeedback
        fields = (
            'gamenight',
            'attendee',
            'game',
            'rating',
        )


class GeneralFeedbackSerializer(serializers.ModelSerializer):
    games = GameFeedbackSerializer(many=True)
    # gamenight = serializers.StringRelatedField(read_only=True)
    # attendee = ContactSerializer()

    class Meta:
        model = GeneralFeedback
        fields = (
            'gamenight',
            'attendee',
            'overall_rating',
            'people_rating',
            'location_rating',
            'games',
        )
        read_only_fields = ['games']

        def create(self, validated_data):
            generalfeedback = GeneralFeedback.objects.create(**validated_data)
            games = validated_data.pop('games')

            for game in games:
                GameFeedback.objects.create(**game, generalfeedback=generalfeedback)
                return generalfeedback



class VotingCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Voting
        fields = (
            'gamenight',
            'invitee',
            'game',
            'vote'
        )
