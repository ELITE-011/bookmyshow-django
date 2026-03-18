from django.db import models
import re


class Genre(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=200)
    duration = models.IntegerField()
    release_date = models.DateField()
    rating = models.FloatField()

    genre = models.ManyToManyField(Genre)
    language = models.ManyToManyField(Language)

    poster = models.URLField(blank=True, null=True)
    
    trailer_url = models.CharField(max_length=255)
    
    def save(self, *args, **kwargs):
        youtube_regex = r"(?:v=|\/)([0-9A-Za-z_-]{11}).*"
        match = re.search(youtube_regex, self.trailer_url)

        if match:
            self.trailer_url = match.group(1)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


# ✅ ADD THIS (Show model - required for seats)
class Show(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    show_time = models.DateTimeField()

    def __str__(self):
        return f"{self.movie.title} - {self.show_time}"

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Movie)
def create_seats(sender, instance, created, **kwargs):
    if created:
        rows = ['A', 'B', 'C', 'D']
        numbers = range(1, 9)

        for row in rows:
            for num in numbers:
                Seat.objects.create(
                    movie=instance,
                    seat_number=f"{row}{num}"
                )

class Seat(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=10)
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.seat_number} - {self.movie.title}"