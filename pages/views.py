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

    print(genre, platform, rating)

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

    if genre:
        if platform:
            if query:
                games_list = api.get_games_test(f'search "{query}"; fields name, cover.url, genres.name; where genres = {str(genres_id)} & platforms = {str(platforms_id)} & rating >= {rating};')
            else:
                games_list = api.get_games_test(f'fields name, cover.url, genres.name; where genres = {str(genres_id)} & platforms = {str(platforms_id)} & rating >= {rating};')
        else:
            if query:
                games_list = api.get_games_test(
                    f'search "{query}"; fields name, cover.url, genres.name; where genres = {str(genres_id)} & rating >= {rating};')
            else:
                games_list = api.get_games_test(
                    f'fields name, cover.url, genres.name; where genres = {str(genres_id)} & rating >= {rating};')
    elif platform:
        if query:
            games_list = api.get_games_test(f'search "{query}"; fields name, cover.url, genres.name; where platforms = {str(platforms_id)} & rating >= {rating};')
        else:
            games_list = api.get_games_test(
                f'fields name, cover.url, genres.name; where platforms = {str(platforms_id)} & rating >= {rating};')
    elif rating:
        if query:
            games_list = api.get_games_test(f'search "{query}"; fields name, cover.url, genres.name; where rating >= {rating};')
        else:
            games_list = api.get_games_test(
                f'fields name, cover.url, genres.name; where rating >= {rating};')
    elif query:
        games_list = api.get_games_test(f'search "{query}"; fields name, cover.url, genres.name;')
    else:
        games_list = []

    games_list = [game for game in games_list if game.get('cover')]

    return render(request, 'index.html', context={
                        'games': games_list,
                        'platforms': platforms_list,
                        'genres': genres_list
                })


def detailed_page(request, id):
    api = IgdbAPI()
    game = api.get_games_test(f'fields name, platforms.name, genres.name,'
                              f' screenshots.url, aggregated_rating, rating,'
                              f' summary, first_release_date; where id = {id};')

    return render(request, 'detailed_page.html', context={'game': game[0]})
