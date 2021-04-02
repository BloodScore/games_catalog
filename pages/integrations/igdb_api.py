import requests
from django.conf import settings


class IgdbAPI:
    def __init__(self):
        self.__url = 'https://api.igdb.com/v4/games'
        self.__headers = {
            'Client-ID': f'{settings.IGDB_CLIENT_ID}',
            'Authorization': f'Bearer {settings.IGDB_ACCESS_TOKEN}'
        }

    def get_games_test(self, data):
        games = requests.post(self.__url, headers=self.__headers, data=data).json()
        return games
