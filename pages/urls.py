from django.urls import path
from . import views


urlpatterns = [
    path('detailed/', views.detailed_page),
    path('', views.index),
]
