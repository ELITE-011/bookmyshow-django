from django.urls import path
from . import views

urlpatterns = [
    path("", views.movie_list, name="movie_list"),
    path("movie/<int:id>/", views.movie_detail, name="movie_detail"),
    path('book/<int:movie_id>/', views.book_ticket, name='book_ticket'),
]
