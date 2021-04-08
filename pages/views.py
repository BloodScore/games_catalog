from django.shortcuts import render
from .integrations.igdb_api import IgdbAPI
from .integrations.twitter_api import TwitterApi


def index(request):
    igdb_api = IgdbAPI()
    query = request.GET.get('q')
    platform = request.GET.get('pl')
    genre = request.GET.get('gn')
    rating = request.GET.get('ra')
    genres_id = []
    platforms_id = []

    platforms_list = [platform for platform in igdb_api.get_platforms()]
    genres_list = [genre for genre in igdb_api.get_genres()]

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

    games_list = igdb_api.get_games_list(body)
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


def detailed_page(request, id, name):
    igdb_api = IgdbAPI()
    game = igdb_api.get_game(id)

    name = name.replace(':', '')

    twitter_api = TwitterApi()
    tweets = twitter_api.get_tweets(name)

    if tweets.get('data'):
        for tweet in tweets['data']:
            tweet['created_at'] = tweet['created_at'][:10] + ' ' + tweet['created_at'][11:19]

            for author in tweets['includes']['users']:
                if author['id'] == tweet['author_id']:
                    tweet['author_nickname'] = author['username']

    return render(request, 'detailed_page.html', context={'game': game[0], 'tweets': tweets})
