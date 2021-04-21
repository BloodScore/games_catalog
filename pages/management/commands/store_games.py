import datetime

from django.core.management.base import BaseCommand
from pages.integrations.igdb_api import IgdbAPI
from pages.models import Game


class Command(BaseCommand):
    help = 'Loads games from IDGBApi with defined offset to database'

    def add_arguments(self, parser):
        parser.add_argument('offset', type=int, help='Indicates the offset for IGDBApi')

    def handle(self, *args, **kwargs):
        offset = kwargs['offset']
        igdb_api = IgdbAPI()
        body = f'fields name, platforms.name, genres.name, screenshots.url, ' \
               f'aggregated_rating, rating, cover.url, summary, first_release_date; limit 500; offset {offset};'

        games_list = igdb_api.get_games_list(body)
        games_list = [game for game in games_list if game.get('cover') and game.get('genres')
                      and game.get('platforms') and game.get('rating')]

        for game in games_list:
            genres = []
            platforms = []
            for genre in game['genres']:
                genres.append(genre['name'])
            for platform in game['platforms']:
                platforms.append(platform['name'])
            game['genres'] = genres
            game['platforms'] = platforms
            if game.get('first_release_date'):
                game['first_release_date'] = datetime.datetime.fromtimestamp(game['first_release_date']).strftime('%d-%m-%Y')

        for game in games_list:
            Game.objects.create(data=game)
