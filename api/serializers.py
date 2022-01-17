from rest_framework import serializers
from .models import Game, CustomUser, GameNight


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


class WishListSerializer(serializers.ModelSerializer):

    class Meta:   
        model = Game
        fields = (
            'pk',
            'bgg',
            'title',
            'pub_year',
            'image',
        )


class GameNightSerializer(serializers.ModelSerializer):

    class Meta:
        model = GameNight
        fields = (
            'date',
            'game',
            'user',
            'player_num',
            'round_num',
            'playtime',
        )