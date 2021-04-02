from django.urls import path
from . import views


urlpatterns = [
    path('detailed/<str:id>', views.detailed_page, name='game_page'),
    path('', views.index),
]
