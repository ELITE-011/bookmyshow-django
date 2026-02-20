from django.contrib import admin
from .models import Movie, Genre, Language

admin.site.register(Genre)
admin.site.register(Language)

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_date', 'rating')