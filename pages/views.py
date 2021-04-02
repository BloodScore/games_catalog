from django.shortcuts import render
from .integrations.igdb_api import IgdbAPI


def index(request):
    api = IgdbAPI()
    games_list = api.get_games_test('fields name, cover.url, genres.name; limit 50;')
    games_list = [game for game in games_list if game.get('cover')]

    return render(request, 'index.html', context={'games': games_list})


def detailed_page(request, id):
    api = IgdbAPI()
    game = api.get_games_test(f'fields name, platforms.name, genres.name,'
                              f' screenshots.url, aggregated_rating, rating,'
                              f' summary, first_release_date; where id = {id};')

    return render(request, 'detailed_page.html', context={'game': game[0]})
