from .models import CustomUser, MustGame, Game, Platform, Genre, Screenshot
from rest_framework import serializers


class CustomUserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'birthday']


class PlatformSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Platform
        fields = ['name']


class GenreSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Genre
        fields = ['name']


class ScreenshotSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Screenshot
        fields = ['url']


class GameSerializer(serializers.HyperlinkedModelSerializer):
    platforms = PlatformSerializer(many=True)
    genres = GenreSerializer(many=True)
    screenshots = ScreenshotSerializer(many=True)

    class Meta:
        model = Game
        fields = [
            'game_id', 'name', 'cover_url', 'summary',
            'first_release_date', 'rating', 'aggregated_rating',
            'platforms', 'genres', 'screenshots'
        ]


class MustGameSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = MustGame
        fields = ['owner', 'game_id', 'users_added', 'is_deleted']
