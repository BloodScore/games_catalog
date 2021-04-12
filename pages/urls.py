from django.urls import path
from . import views


urlpatterns = [
    path('register', views.register, name='register_page'),
    path('login', views.login_user, name='login'),
    path('logout', views.logout_user, name='logout'),
    path('profile', views.profile, name='profile'),
    path('detailed/<str:id>', views.detailed_page, name='game_page'),
    path('', views.index, name='games_list_page'),
]
