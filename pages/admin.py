from django.contrib import admin
from .models import CustomUser, MustGame, Game


admin.site.register(CustomUser)
admin.site.register(MustGame)
admin.site.register(Game)
