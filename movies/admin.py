from django.contrib import admin
from .models import Movie, Genre, Language, Seat, Booking

admin.site.register(Genre)
admin.site.register(Language)
admin.site.register(Seat)
admin.site.register(Booking)

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_date', 'rating')