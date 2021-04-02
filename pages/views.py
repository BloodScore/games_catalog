from django.shortcuts import render
from .integrations.igdb_api import IgdbAPI
import json


def index(request):
    api = IgdbAPI()
    games_list = json.loads(api.get_games_test('fields name, cover.url, genres.name; limit 50;').text)
    data = []

    for game in games_list:
        if 'cover' in game:
            # url = game['cover']['url'].replace('t_thumb', 'cover_big')
            genres = []
            if 'genres' in game:
                for i in game['genres']:
                    genres.append(i['name'])
            if len(genres) > 3:
                genres = genres[:3]

            data.append({'id': game['id'], 'name': game['name'],
                         'cover': game['cover']['url'], 'genres': genres})
        else:
            data.append({'id': game['id'], 'name': game['name'], 'cover': 'https://via.placeholder.com/280'})

    return render(request, 'index.html', context={'games': data})


def detailed_page(request, id):
    api = IgdbAPI()
    game = json.loads(api.get_games_test(f'fields name, platforms.name, genres.name,'
                                         f' screenshots.url, aggregated_rating, rating,'
                                         f' summary, first_release_date; where id = {id};').text)

    return render(request, 'detailed_page.html', context={'game': game[0]})
