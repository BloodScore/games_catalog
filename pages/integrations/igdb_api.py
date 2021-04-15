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

    def get_game(self, id):
        body = f'fields name, platforms.name, genres.name, screenshots.url, ' \
               f'aggregated_rating, rating, cover.url, summary, first_release_date; where id = {id};'
        game = requests.post(self.__url_games, headers=self.__headers, data=body).json()
        return game

    def get_games_list(self, body):
        games = requests.post(self.__url_games, headers=self.__headers, data=body).json()
        return games

    def get_platforms(self):
        body = 'fields name; limit 500;'
        platforms = requests.post(self.__url_platforms, headers=self.__headers, data=body).json()
        return platforms

    def get_genres(self):
        body = 'fields name; limit 500;'
        genres = requests.post(self.__url_genres, headers=self.__headers, data=body).json()
        return genres
