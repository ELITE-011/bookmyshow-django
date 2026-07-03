from django.urls import path
from . import views

urlpatterns = [
    path("", views.movie_list, name="movie_list"),
    path("movie/<int:id>/", views.movie_detail, name="movie_detail"),
    path("admin-dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("export-bookings-csv/", views.export_bookings_csv, name="export_bookings_csv"),
    path('book/<int:movie_id>/', views.book_ticket, name='book_ticket'),
    path('seats/<int:movie_id>/', views.seat_selection, name='seat_selection'),
    path('pay/', views.create_checkout_session, name='pay'),
    path('success/', views.success, name='success'),
    path('cancel/', views.cancel, name='cancel'),
    path('release-reservation/', views.release_reservation, name='release_reservation'),
    path('reset-seats/', views.reset_seats, name='reset_seats'),
    path('test-email/', views.test_email, name='test_email'),
    path(
    'export-bookings/',
    views.export_bookings_csv,
    name='export_bookings_csv'
),
]
