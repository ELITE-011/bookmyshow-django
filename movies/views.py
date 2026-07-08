import csv
import json
from datetime import timedelta

import stripe
import resend
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.core.mail import send_mail
from django.db.models import Count, Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .models import Booking, Genre, Language, Movie, Seat, Show

def movie_list(request):
    movies = Movie.objects.all()
    
    search_query = request.GET.get("search")
    selected_genre = request.GET.get('genre')
    selected_language = request.GET.get('language')

    if selected_genre:
        movies = movies.filter(genre__name=selected_genre)

    if selected_language:
        movies = movies.filter(language__name=selected_language)
        
    if search_query:
        movies = movies.filter(
            Q(title__icontains=search_query)
    )

    movies = movies.distinct()

    context = {
        "movies": movies,
        "genres": Genre.objects.all(),
        "languages": Language.objects.all(),
        "selected_genre": selected_genre,
        "selected_language": selected_language,
        "search_query": search_query,
    }

    return render(request, "movies/movie_list.html", context)  


def movie_detail(request, id):
    movie = get_object_or_404(Movie, id=id)

    return render(request, "movies/movie_detail.html", {
        "movie": movie
    })
    

def book_ticket(request, movie_id):

    movie = get_object_or_404(Movie, id=movie_id)

    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        seats = request.POST.getlist("seats")
        seats_str = ", ".join(seats)

        booking = Booking.objects.create(
            name=name,
            email=email,
            movie=movie,
            seats=seats_str,
            payment_status='Pending'
        )

  # Reserve selected seats for 5 minutes
        for seat_no in seats:
            Seat.objects.filter(
                movie=movie,
                seat_number=seat_no
            ).update(
                is_reserved=True,
                reserved_until=timezone.now() + timedelta(minutes=5)
            )

        request.session['booking_id'] = booking.id

        return redirect('pay')

    return render(request, "movies/book_ticket.html", {"movie": movie})


def seat_selection(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)

    # Release expired reservations
    expired_seats = Seat.objects.filter(
        movie=movie,
        is_reserved=True,
        reserved_until__lt=timezone.now(),
        is_booked=False
    )

    expired_seats.update(
        is_reserved=False,
        reserved_until=None
    )

    all_seats = Seat.objects.filter(movie=movie)

    seat_map = []

    for row in ["A", "B", "C", "D"]:
        row_seats = []

        for i in range(1, 9):
            seat = all_seats.get(seat_number=f"{row}{i}")
            row_seats.append(seat)

        seat_map.append(row_seats)

    return render(
        request,
        "movies/seat_selection.html",
        {
            "movie": movie,
            "seat_map": seat_map,
        },
    )

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_checkout_session(request):
    domain_url = request.build_absolute_uri('/')[:-1]

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'inr',
                'product_data': {
                    'name': 'Movie Ticket',
                },
                'unit_amount': 20000,  # ₹200
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=domain_url + '/success/',
        cancel_url=domain_url + '/cancel/',
    )

    return redirect(session.url)   

print("1. SUCCESS START")

def success(request):
    print("SUCCESS PAGE OPENED")

    booking_id = request.session.get("booking_id")

    if not booking_id:
        print("NO BOOKING ID")
        return render(request, "movies/payment_success.html")

    try:
        booking = Booking.objects.get(id=booking_id)
        print("2. BOOKING FOUND")
    except Booking.DoesNotExist:
        print("BOOKING NOT FOUND")
        return render(request, "movies/payment_success.html")

    print("Booking ID:", booking.id)
    print("Current Status:", booking.payment_status)

    if booking.payment_status == "Pending":

        booking.payment_status = "Paid"
        booking.save()
        print("3. BOOKING SAVED")

        booking.refresh_from_db()
        print("Payment Status After Save:", booking.payment_status)

        seat_numbers = [
            seat.strip()
            for seat in booking.seats.split(",")
            if seat.strip()
        ]

        Seat.objects.filter(
            movie=booking.movie,
            seat_number__in=seat_numbers
        ).update(
            is_booked=True,
            is_reserved=False,
            reserved_until=None
        )

        print("4. SEATS UPDATED")

        message = f"""
Hello {booking.name},

Your booking is confirmed!

Movie: {booking.movie.title}
Seats: {booking.seats}

Enjoy your movie experience 🎬🍿
"""

        print("SENDING EMAIL...")

        try:
            resend.api_key = settings.RESEND_API_KEY

            response = resend.Emails.send({
                "from": "BookMyShow <onboarding@resend.dev>",
                "to": [booking.email],
                "subject": "Ticket Confirmation",
                "text": message,
            })

            print("EMAIL SENT SUCCESSFULLY")
            print(response)

        except Exception as e:
            print("EMAIL ERROR:", repr(e))

    print("7. RETURNING SUCCESS PAGE")

    return render(
        request,
        "movies/payment_success.html",
        {
            "booking": booking,
        },
    )
 
def cancel(request):
    return render(request, "movies/payment_cancel.html")

def test_email(request):

    try:

        resend.api_key = settings.RESEND_API_KEY

        response = resend.Emails.send({
            "from": "BookMyShow <onboarding@resend.dev>",
            "to": ["deepj3071@gmail.com"],
            "subject": "Test Email",
            "text": "Hello Deep! Resend is working successfully."
        })

        print(response)

        return HttpResponse("Email Sent Successfully")

    except Exception as e:

        print("EMAIL ERROR:", repr(e))

        return HttpResponse("Email failed.")
    

def release_reservation(request):

    booking_id = request.session.get("booking_id")

    if not booking_id:
        return JsonResponse({"status": "no booking"})

    try:
        booking = Booking.objects.get(id=booking_id)

        if booking.payment_status == "Pending":

            seat_numbers = booking.seats.split(",")

            for seat in seat_numbers:
                Seat.objects.filter(
                    movie=booking.movie,
                    seat_number=seat.strip()
                ).update(
                    is_reserved=False,
                    reserved_until=None
                )

            booking.delete()

    except Booking.DoesNotExist:
        pass

    return JsonResponse({"status": "released"})

def reset_seats(request):

    Seat.objects.all().update(
        is_booked=False,
        is_reserved=False,
        reserved_until=None
    )

    Booking.objects.all().delete()

    return HttpResponse(
        "<h2>✅ All seats and bookings have been reset successfully.</h2>"
        "<br><a href='/'>Go to Home</a>"
    )
   

@staff_member_required
def admin_dashboard(request):

    total_bookings = Booking.objects.filter(
        payment_status="Paid"
    ).count()

    paid_bookings = Booking.objects.filter(payment_status="Paid")

    total_tickets = 0

    for booking in paid_bookings:
        total_tickets += len(booking.seats.split(","))

    total_revenue = total_tickets * 200

    total_movies = Movie.objects.count()

    total_shows = Show.objects.count()

    total_seats = Seat.objects.count()
    popular_movies = (
    Booking.objects
    .filter(payment_status="Paid")
    .values("movie__title")
    .annotate(total_bookings=Count("id"))
    .order_by("-total_bookings")[:5]
)
    recent_bookings = Booking.objects.select_related("movie").order_by("-booking_date")[:10]
    
    
    movie_labels = [movie["movie__title"] for movie in popular_movies]
    movie_counts = [movie["total_bookings"] for movie in popular_movies]

    paid_count = Booking.objects.filter(payment_status="Paid").count()
    pending_count = Booking.objects.filter(payment_status="Pending").count()

    context = {
    "total_revenue": total_revenue,
    "total_bookings": total_bookings,
    "total_movies": total_movies,
    "total_shows": total_shows,
    "total_seats": total_seats,

    "popular_movies": popular_movies,
    "recent_bookings": recent_bookings,

    "movie_labels": json.dumps(movie_labels),
    "movie_counts": json.dumps(movie_counts),

    "paid_count": paid_count,
    "pending_count": pending_count,
}

    return render(
        request,
        "movies/admin_dashboard.html",
        context
    )
    
    

@staff_member_required
def export_bookings_csv(request):

    response = HttpResponse(content_type='text/csv')

    response['Content-Disposition'] = 'attachment; filename="bookings.csv"'

    writer = csv.writer(response)

    writer.writerow([
        'Customer',
        'Movie',
        'Seats',
        'Payment Status',
        'Booking Date'
    ])

    bookings = Booking.objects.select_related('movie').all()

    for booking in bookings:

        writer.writerow([
            booking.name,
            booking.movie.title,
            booking.seats,
            booking.payment_status,
            booking.booking_date.strftime("%d-%m-%Y %H:%M")
        ])

    return response