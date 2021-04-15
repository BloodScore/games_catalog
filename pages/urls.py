from django.urls import path, re_path
from . import views


urlpatterns = [
    path('register', views.register, name='register_page'),
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$',
            views.activate, name='activate'),
    path('account_activation_sent', views.account_activation_sent, name='account_activation_sent'),
    path('login', views.login_user, name='login'),
    path('logout', views.logout_user, name='logout'),
    path('profile', views.profile, name='profile'),
    path('email_to_reset_password', views.email_to_reset_password, name='email_to_reset_password'),
    path('reset_password_mail_sent', views.reset_password_mail_sent, name='reset_password_mail_sent'),
    re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$',
            views.reset_password, name='reset'),
    path('update_profile', views.update_profile, name='update_profile'),
    path('delete_profile', views.delete_profile, name='delete_profile'),
    path('detailed/<str:id>', views.detailed_page, name='game_page'),
    path('favourite_games', views.fav_games, name='fav_games'),
    path('must/<str:id>', views.must, name='must'),
    path('unmust/<str:id>', views.unmust, name='unmust'),
    path('', views.index, name='games_list_page'),
]
