from django.shortcuts import render
from .models import Movie, Genre, Language

def movie_list(request):
    movies = Movie.objects.all()

    selected_genre = request.GET.get('genre')
    selected_language = request.GET.get('language')

    if selected_genre:
        movies = movies.filter(genre__name=selected_genre)

    if selected_language:
        movies = movies.filter(language__name=selected_language)

    movies = movies.distinct()

    return render(request, "movies/movie_list.html", {
        "movies": movies,
        "genres": Genre.objects.all(),
        "languages": Language.objects.all(),
    })