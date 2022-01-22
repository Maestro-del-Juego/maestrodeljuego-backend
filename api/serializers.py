from rest_framework import serializers
from .models import Game, CustomUser, Tag, GameNight, Contact, Voting
from djoser.serializers import UserCreatePasswordRetypeSerializer


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


class GameForGameNightSerializer(serializers.ModelSerializer):
    votes = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = (
            'pk',
            'bgg',
            'title',
            'pub_year',
            'image',
            'votes',
        )

    def get_votes(self, obj):
        # view = self.context.get('view')
        # # breakpoint()
        # rid = view.kwargs['rid']
        # gamenight = GameNight.objects.get(rid=rid)
        # votes = obj.tally_votes(gamenight)
        # return votes
        return 0


class GameNightSerializer(serializers.ModelSerializer):
    user = UserNestedSerializer(read_only=True)
    invitees = ContactSerializer(many=True)
    attendees = ContactSerializer(many=True)
    games = GameListSerializer(read_only=True, many=True)
    options = GameForGameNightSerializer(read_only=True, many=True)

    class Meta:
        model = GameNight
        fields = (
            'pk',
            'rid',
            'user',
            'date',
            'invitees',
            'attendees',
            'games',
            'start_time',
            'end_time',
            'location',
            'options'
        )


class GameNightCreateSerializer(serializers.ModelSerializer):
    user = UserNestedSerializer(read_only=True)

    class Meta:
        model = GameNight
        fields = (
            'pk',
            'rid',
            'user',
            'date',
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


class VotingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Voting
        fields = (
            'gamenight',
            'invitee',
            'game',
            'vote'
        )