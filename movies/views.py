from django.shortcuts import render
from .models import Movie, Genre, Language

def movie_list(request):
    movies = Movie.objects.all()

    selected_genres = request.GET.getlist('genre')
    selected_languages = request.GET.getlist('language')

    if selected_genres:
        movies = movies.filter(genre__name__in=selected_genres)

    if selected_languages:
        movies = movies.filter(language__name__in=selected_languages)

    movies = movies.distinct()

    return render(request, "movies/movie_list.html", {
        "movies": movies,
        "genres": Genre.objects.all(),
        "languages": Language.objects.all(),
    })