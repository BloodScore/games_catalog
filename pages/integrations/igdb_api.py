import requests
from django.conf import settings


class IgdbAPI:
    def __init__(self):
        self.__url_games = 'https://api.igdb.com/v4/games'
        self.__url_platforms = 'https://api.igdb.com/v4/platforms'
        self.__url_genres = 'https://api.igdb.com/v4/genres'
        self.__headers = {
            'Client-ID': f'{settings.IGDB_CLIENT_ID}',
            'Authorization': f'Bearer {settings.IGDB_ACCESS_TOKEN}'
        }

    def get_games_test(self, data):
        games = requests.post(self.__url_games, headers=self.__headers, data=data).json()
        return games

    def get_platforms(self):
        data = 'fields name; limit 500;'
        platforms = requests.post(self.__url_platforms, headers=self.__headers, data=data).json()
        return platforms

    def get_genres(self):
        data = 'fields name; limit 500;'
        genres = requests.post(self.__url_genres, headers=self.__headers, data=data).json()
        return genres
