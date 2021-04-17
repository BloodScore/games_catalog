from django.contrib.auth import login, logout, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import F
from django.http import HttpResponse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .integrations.igdb_api import IgdbAPI
from .integrations.twitter_api import TwitterApi
from .forms import CreateCustomUserForm, LoginForm, CustomUserInfoForm, EmailForm, PasswordResetForm, \
    CustomUserChangeForm
from .tokens import account_activation_token, password_reset_token
from .models import CustomUser, MustGame


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
    if request.user.is_authenticated:
        return redirect('games_list_page')

    if request.method == 'POST':
        form = CreateCustomUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.save()
            domain, uid, token = create_mail_link(request, user, 'activate')
            link = f'http://{domain}/activate/{uid}/{token}/'
            send_mail(
                'GameMuster Verification mail',
                f'Hello, {user.username}! Thanks for registration! Click this link to activate your account: {link}',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False
            )
            return redirect('account_activation_sent')
    else:
        form = CreateCustomUserForm()

    return render(request, 'register.html', context={'form': form})


def login_user(request):
    if request.user.is_authenticated:
        return redirect('games_list_page')

    if request.method == 'POST':
        next_url = request.POST.get('next')
        form = LoginForm(request.POST)
        if form.is_valid():
            credentials = form.cleaned_data
            user = authenticate(request, username=credentials['username'], password=credentials['password'])
            if user:
                login(request, user)
                if next_url:
                    return redirect(next_url)
                else:
                    return redirect('games_list_page')
            else:
                messages.info(request, 'Username or password is incorrect!')
    else:
        form = LoginForm()

    return render(request, 'login.html', context={'form': form})


def account_activation_sent(request):
    return render(request, 'account_activation_sent.html')


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('games_list_page')


def logout_user(request):
    logout(request)
    return redirect('games_list_page')


@login_required
def profile(request):
    form = CustomUserInfoForm(instance=request.user)
    return render(request, 'profile.html', context={'form': form})


def email_to_reset_password(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            user = CustomUser.objects.get(email=email)
            domain, uid, token = create_mail_link(request, user, 'reset')
            link = f'http://{domain}/reset/{uid}/{token}/'
            send_mail(
                'GameMuster password reset mail',
                f'Hello, {user.username}! Click this link to go to password reset page: {link}',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False
            )
            return redirect('reset_password_mail_sent')
    else:
        form = EmailForm()
    return render(request, 'email_form.html', context={'form': form})


def reset_password_mail_sent(request):
    return render(request, 'reset_password_mail_sent.html')


def reset_password(request, uidb64, token):
    if request.method == 'POST':
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password1']
            print(password)
            try:
                uid = force_text(urlsafe_base64_decode(uidb64))
                user = CustomUser.objects.get(pk=uid)
            except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
                user = None

            if user and password_reset_token.check_token(user, token):
                user.set_password(password)
                user.save()
                return redirect('login')
    else:
        form = PasswordResetForm()
    return render(request, 'reset_password.html', context={'form': form, 'uidb64': uidb64, 'token': token})


def create_mail_link(request, user, what_for):
    domain = get_current_site(request).domain
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    if what_for == 'activate':
        token = account_activation_token.make_token(user)
    else:
        token = password_reset_token.make_token(user)
    return domain, uid, token


@login_required
def update_profile(request):
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = CustomUserChangeForm(instance=request.user)

    return render(request, 'update_profile.html', context={'form': form})


@login_required
def delete_profile(request):
    user = request.user
    if request.method == 'POST':
        user.delete()
        return redirect('games_list_page')

    return render(request, 'delete_profile.html')


@login_required
def fav_games(request):
    igdb_api = IgdbAPI()
    must_games = MustGame.objects.filter(owner=request.user, is_deleted=False)
    games = []

    for must_game in must_games:
        game = igdb_api.get_game(must_game.game_id)[0]
        game['users_added'] = must_game.users_added
        games.append(game)

    return render(request, 'fav_games.html', context={'games': games})


@login_required
def must(request):
    id = request.POST.get('game_id')
    users_added = len(MustGame.objects.filter(game_id=id, is_deleted=False))

    must_game, created = MustGame.objects.get_or_create(owner=request.user, game_id=id, users_added=users_added)
    
    if created:
        MustGame.objects.filter(game_id=id).update(users_added=F('users_added') + 1)
    elif must_game.is_deleted:
        must_game.is_deleted = False
        must_game.save()
        MustGame.objects.filter(game_id=id).update(users_added=F('users_added') + 1)

    return HttpResponse(status=200)


@login_required
def unmust(request):
    id = request.POST.get('game_id')
    MustGame.objects.filter(owner=request.user, game_id=id).update(is_deleted=True)
    MustGame.objects.filter(game_id=id).update(users_added=F('users_added') - 1)
    return HttpResponse(status=200)
