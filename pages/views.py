from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.contrib import messages
from .integrations.igdb_api import IgdbAPI
from .integrations.twitter_api import TwitterApi
from .forms import CreateCustomUserForm, LoginForm, CustomUserInfoForm


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


def detailed_page(request, id):
    igdb_api = IgdbAPI()
    game = igdb_api.get_game(id)

    name = game[0]['name'].replace(':', '')

    twitter_api = TwitterApi()
    tweets = twitter_api.get_tweets(name)

    if tweets.get('data'):
        for tweet in tweets['data']:
            tweet['created_at'] = tweet['created_at'][:10] + ' ' + tweet['created_at'][11:19]

            for author in tweets['includes']['users']:
                if author['id'] == tweet['author_id']:
                    tweet['author_nickname'] = author['username']

    return render(request, 'detailed_page.html', context={'game': game[0], 'tweets': tweets})


def register(request):
    if request.method == 'POST':
        form = CreateCustomUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CreateCustomUserForm()

    return render(request, 'register.html', context={'form': form})


def login_user(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            credentials = form.cleaned_data
            user = authenticate(request, username=credentials['username'], password=credentials['password'])
            if user:
                login(request, user)
                return redirect('games_list_page')
            else:
                messages.info(request, 'Username or password is incorrect!')
    else:
        form = LoginForm()

    return render(request, 'login.html', context={'form': form})


def logout_user(request):
    logout(request)
    return redirect('games_list_page')


def profile(request):
    form = CustomUserInfoForm(instance=request.user)
    return render(request, 'profile.html', context={'form': form})
