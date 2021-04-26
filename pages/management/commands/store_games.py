import datetime

from django.core.management.base import BaseCommand
from pages.integrations.igdb_api import IgdbAPI
from pages.models import Game, Genre, Platform, Screenshot


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
        games_list = [
            game for game in games_list if all([
                            game.get('cover'),
                            game.get('genres'),
                            game.get('platforms'),
                            game.get('rating')
                        ])
        ]

        for game in games_list:
            created_game = Game.objects.create(
                name=game['name'],
                game_id=game['id'],
                cover_url=game['cover']['url'],
                summary=game['summary'] if game.get('summary') else '',
                first_release_date=datetime.datetime.fromtimestamp(game['first_release_date']).strftime('%Y-%m-%d')
                                                                    if game.get('first_release_date') else None,
                rating=game['rating'],
                aggregated_rating=game['aggregated_rating'] if game.get('aggregated_rating') else 0
            )

            for genre in game['genres']:
                genre_object, created = Genre.objects.get_or_create(name=genre['name'])
                created_game.genres.add(genre_object)

            for platform in game['platforms']:
                platform_object, created = Platform.objects.get_or_create(name=platform['name'])
                created_game.platforms.add(platform_object)

            if game.get('screenshots'):
                for screenshot in game['screenshots']:
                    screenshot_object, created = Screenshot.objects.get_or_create(url=screenshot['url'])
                    created_game.screenshots.add(screenshot_object)
