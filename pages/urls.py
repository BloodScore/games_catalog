from django.urls import path
from . import views


urlpatterns = [
    path('detailed/<str:id>/<str:name>', views.detailed_page, name='game_page'),
    path('', views.index, name='games_list_page'),
]
