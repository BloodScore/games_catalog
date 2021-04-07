from django.shortcuts import render
from .integrations.igdb_api import IgdbAPI


def index(request):
    api = IgdbAPI()
    query = request.GET.get('q')
    platform = request.GET.get('pl')
    genre = request.GET.get('gn')
    rating = request.GET.get('ra')
    genres_id = []
    platforms_id = []

    platforms_list = [platform for platform in api.get_platforms()]
    genres_list = [genre for genre in api.get_genres()]

    if genre:
        for genre_name in genre.split(','):
            for i in genres_list:
                if i.get('name') == genre_name:
                    genres_id.append(i.get('id'))
                    break

    if platform:
        for platform_name in platform.split(','):
            for i in platforms_list:
                if i.get('name') == platform_name:
                    platforms_id.append(i.get('id'))
                    break

    platforms_filter = f'platforms = {str(platforms_id)};' if platform else ''
    genres_filter = f'genres = {str(genres_id)};' if genre else ''
    rating_filter = f'rating >= {rating};' if rating else ''
    query_filter = f'search "{query}";' if query else ''
    where_string = ''
    fields_string = 'fields name, cover.url, genres.name;'

    if platforms_filter and (genres_filter or rating_filter):
        platforms_filter = platforms_filter[:-1]
        platforms_filter += '&'

    if genres_filter and rating_filter:
        genres_filter = genres_filter[:-1]
        genres_filter += '&'

    if platforms_filter or genres_filter or rating_filter:
        where_string = 'where '

    body = f'{query_filter}{where_string}{platforms_filter}{genres_filter}{rating_filter}{fields_string}'

    games_list = api.get_games_list(body)
    games_list = [game for game in games_list if game.get('cover')]

    return render(request, 'index.html', context={
                        'games': games_list,
                        'platforms': platforms_list,
                        'genres': genres_list,
                        'query': query,
                        'platform': platform,
                        'genre': genre,
                        'rating': rating,
                })


def detailed_page(request, id):
    api = IgdbAPI()
    game = api.get_game(id)

    return render(request, 'detailed_page.html', context={'game': game[0]})
