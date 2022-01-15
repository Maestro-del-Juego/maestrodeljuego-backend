from rest_framework import serializers
from .models import Game, CustomUser


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
        )
