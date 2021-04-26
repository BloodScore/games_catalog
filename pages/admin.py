from django.contrib import admin
from .models import CustomUser, MustGame, Game, Screenshot, Platform, Genre


admin.site.register(CustomUser)
admin.site.register(MustGame)
admin.site.register(Game)
admin.site.register(Screenshot)
admin.site.register(Platform)
admin.site.register(Genre)
