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

    def get_votes(self):
        return 0


class GameNightSerializer(serializers.ModelSerializer):
    user = UserNestedSerializer(read_only=True)
    invitees = ContactSerializer(many=True)
    attendees = ContactSerializer(many=True)
    games = serializers.SlugRelatedField(read_only=True, many=True, slug_field="title")
    option1 = GameForGameNightSerializer(read_only=True)
    option2 = GameForGameNightSerializer(read_only=True)
    option3 = GameForGameNightSerializer(read_only=True)
    option4 = GameForGameNightSerializer(read_only=True)
    option5 = GameForGameNightSerializer(read_only=True)
    option6 = GameForGameNightSerializer(read_only=True)
    option7 = GameForGameNightSerializer(read_only=True)
    option8 = GameForGameNightSerializer(read_only=True)
    option9 = GameForGameNightSerializer(read_only=True)
    option10 = GameForGameNightSerializer(read_only=True)
    class Meta:
        model = GameNight
        fields = (
            'pk',
            'user',
            'date',
            'invitees',
            'attendees',
            'games',
            'start_time',
            'end_time',
            'location',
            'option1',
            'option2',
            'option3',
            'option4',
            'option5',
            'option6',
            'option7',
            'option8',
            'option9',
            'option10'
        )


class GameNightCreateSerializer(serializers.ModelSerializer):
    user = UserNestedSerializer(read_only=True)

    class Meta:
        model = GameNight
        fields = (
            'user',
            'date',
            'invitees',
            'games',
            'start_time',
            'end_time',
            'location',
            'option1',
            'option2',
            'option3',
            'option4',
            'option5',
            'option6',
            'option7',
            'option8',
            'option9',
            'option10'
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
            'option1',
            'option2',
            'option3',
            'option4',
            'option5',
            'option6',
            'option7',
            'option8',
            'option9',
            'option10',
        )
