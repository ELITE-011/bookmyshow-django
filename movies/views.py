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

    context = {
        "movies": movies,
        "genres": Genre.objects.all(),
        "languages": Language.objects.all(),
        "selected_genre": selected_genre,
        "selected_language": selected_language,
    }

    return render(request, "movies/movie_list.html", context)  

from django.shortcuts import get_object_or_404

def movie_detail(request, id):
    movie = get_object_or_404(Movie, id=id)

    return render(request, "movies/movie_detail.html", {
        "movie": movie
    })