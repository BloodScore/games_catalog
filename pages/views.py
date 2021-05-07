from django.contrib.auth import login, logout, authenticate
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import F
from django.http import HttpResponse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from rest_framework import permissions, status
from rest_framework.decorators import api_view
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .integrations.igdb_api import IgdbAPI
from .integrations.twitter_api import TwitterApi
from .forms import CreateCustomUserForm, LoginForm, CustomUserInfoForm, EmailForm, PasswordResetForm, \
    CustomUserChangeForm
from .tokens import account_activation_token, password_reset_token
from .models import CustomUser, MustGame, Game
from .serializers import CustomUserSerializer, GameSerializer, MustGameSerializer


GAMES_PER_PAGE = 12


def index(request):
    igdb_api = IgdbAPI()
    query = request.GET.get('q')
    platform = request.GET.get('pl')
    genre = request.GET.get('gn')
    rating = request.GET.get('ra')
    page = request.GET.get('page')

    platforms_list = [platform for platform in igdb_api.get_platforms()]
    genres_list = [genre for genre in igdb_api.get_genres()]

    if query or genre or platform or rating:
        games_list = Game.objects.filter(
                                        name__icontains=query if query else ''
                                    ).filter(
                                        rating__gte=int(rating) if rating else 1
                                    )

        if genre:
            temp_list = []
            for game in games_list:
                game_genres = set()
                for genre_object in game.genres.all():
                    game_genres.add(genre_object.name)
                if len(set(genre.split(',')).intersection(game_genres)) == len(genre.split(',')):
                    temp_list.append(game)
            games_list = temp_list[:]

        if platform:
            temp_list = []
            for game in games_list:
                game_platforms = set()
                for platform_object in game.platforms.all():
                    game_platforms.add(platform_object.name)
                if len(set(platform.split(',')).intersection(game_platforms)) == len(platform.split(',')):
                    temp_list.append(game)
            games_list = temp_list[:]

    else:
        games_list = Game.objects.all()

    paginator = Paginator(games_list, GAMES_PER_PAGE)
    try:
        games_list = paginator.page(page)
    except PageNotAnInteger:
        games_list = paginator.page(1)
    except EmptyPage:
        games_list = paginator.page(paginator.num_pages)

    return render(request, 'index.html', context={
                        'games': games_list,
                        'platforms': platforms_list,
                        'genres': genres_list,
                        'query': query,
                        'platform': platform,
                        'genre': genre,
                        'rating': rating,
                })


def detailed_page(request, game_id):
    game = Game.objects.filter(game_id=int(game_id))[0]

    name = game.name.replace(':', '')

    twitter_api = TwitterApi()
    tweets = twitter_api.get_tweets(name)

    if tweets.get('data'):
        for tweet in tweets['data']:
            tweet['created_at'] = tweet['created_at'][:10] + ' ' + tweet['created_at'][11:19]

            for author in tweets['includes']['users']:
                if author['id'] == tweet['author_id']:
                    tweet['author_nickname'] = author['username']

    return render(request, 'detailed_page.html', context={'game': game, 'tweets': tweets})


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
    page = request.GET.get('page')
    must_games = MustGame.objects.filter(owner=request.user, is_deleted=False)
    games = []

    for must_game in must_games:
        game = Game.objects.filter(game_id=must_game.game_id)[0]
        game.users_added = must_game.users_added
        games.append(game)

    paginator = Paginator(games, GAMES_PER_PAGE)
    try:
        games = paginator.page(page)
    except PageNotAnInteger:
        games = paginator.page(1)
    except EmptyPage:
        games = paginator.page(paginator.num_pages)

    return render(request, 'fav_games.html', context={'games': games})


@login_required
def must(request):
    game_id = request.POST.get('game_id')
    users_added = MustGame.objects.filter(game_id=game_id, is_deleted=False).count()

    must_game, created = MustGame.objects.get_or_create(owner=request.user, game_id=game_id, users_added=users_added)
    
    if created:
        MustGame.objects.filter(game_id=game_id).update(users_added=F('users_added') + 1)
    elif must_game.is_deleted:
        must_game.is_deleted = False
        must_game.save()
        MustGame.objects.filter(game_id=game_id).update(users_added=F('users_added') + 1)

    return HttpResponse(status=200)


@login_required
def unmust(request):
    game_id = request.POST.get('game_id')
    MustGame.objects.filter(owner=request.user, game_id=game_id).update(is_deleted=True)
    MustGame.objects.filter(game_id=game_id).update(users_added=F('users_added') - 1)
    return HttpResponse(status=200)


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'profile': reverse('api_profile', request=request, format=format),
        'games': reverse('api_games', request=request, format=format),
        'must_games': reverse('api_must_games', request=request, format=format),
        'must_game_detailed': reverse('api_game', args=[20950], request=request),
    })


class CustomUserView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = CustomUserSerializer(request.user)
        return Response(serializer.data)


class GameListView(APIView, LimitOffsetPagination):
    def get(self, request):
        games = Game.objects.all()
        results = self.paginate_queryset(games, request, view=self)
        serializer = GameSerializer(results, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)


class GameDetailedView(APIView):
    def get(self, request, pk):
        games = Game.objects.filter(game_id=int(pk))
        if not games:
            return Response({'message': 'Game does not exist!'}, status=status.HTTP_404_NOT_FOUND)
        serializer = GameSerializer(games[0], context={'request': request})
        return Response(serializer.data)


class MustGameListView(APIView, LimitOffsetPagination):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        must_games_objects = MustGame.objects.filter(owner=request.user, is_deleted=False)

        must_games_ids = [must_game.game_id for must_game in must_games_objects]

        users_must_games = [Game.objects.get(game_id=game_id) for game_id in must_games_ids]
        results = self.paginate_queryset(users_must_games, request, view=self)
        serializer = GameSerializer(results, many=True, context={'request': request})
        return self.get_paginated_response(serializer.data)

    def post(self, request):
        game_id = request.data.get('game_id')
        try:
            must_games = MustGame.objects.filter(owner=request.user, game_id=int(game_id), is_deleted=False)
        except (TypeError, ValueError):
            return Response({'message': 'Game id is missing or incorrect'}, status=status.HTTP_400_BAD_REQUEST)

        games = Game.objects.filter(game_id=int(game_id))
        if not games:
            return Response({'message': 'Game does not exist!'}, status=status.HTTP_404_NOT_FOUND)

        if not must_games:
            must_games_objects = MustGame.objects.filter(owner=request.user, game_id=int(game_id))

            data = {
                'game_id': int(game_id),
                'users_added': MustGame.objects.filter(game_id=game_id, is_deleted=False).count() + 1,
                'is_deleted': False
            }

            if must_games_objects:
                serializer = MustGameSerializer(must_games_objects[0], data=data, context={'request': request})
            else:
                serializer = MustGameSerializer(data=data, context={'request': request})

            MustGame.objects.filter(game_id=int(game_id)).exclude(owner=request.user).update(users_added=F('users_added') + 1)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            MustGame.objects.filter(game_id=int(game_id)).update(users_added=F('users_added') - 1)
            MustGame.objects.filter(game_id=int(game_id), owner=request.user).update(is_deleted=True)
            return Response({'message': f'Must game with id {game_id} has been deleted.'}, status=status.HTTP_204_NO_CONTENT)
