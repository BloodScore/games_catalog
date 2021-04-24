from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    birthday = models.DateField(null=True)

    def __str__(self):
        return self.username


class MustGame(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    game_id = models.IntegerField(null=False)
    is_deleted = models.BooleanField(default=False)
    users_added = models.IntegerField(default=0)


class Platform(models.Model):
    name = models.CharField(max_length=64)


class Genre(models.Model):
    name = models.CharField(max_length=64)


class Screenshot(models.Model):
    url = models.URLField(blank=True, null=True)


class Game(models.Model):
    name = models.CharField(max_length=100)
    game_id = models.IntegerField(null=False)
    cover_url = models.URLField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    first_release_date = models.DateField(blank=True, null=True)
    rating = models.FloatField(blank=True, null=True)
    aggregated_rating = models.FloatField(blank=True, null=True)
    users_added = models.IntegerField(default=0)

    platforms = models.ManyToManyField(Platform, related_name='games')
    genres = models.ManyToManyField(Genre, related_name='games')
    screenshots = models.ManyToManyField(Screenshot, related_name='games')
