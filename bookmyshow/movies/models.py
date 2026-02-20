from django.db import models

class Movie(models.Model):

    GENRE_CHOICES = [
        ('Action', 'Action'),
        ('Comedy', 'Comedy'),
        ('Drama', 'Drama'),
        ('Horror', 'Horror'),
    ]

    LANGUAGE_CHOICES = [
        ('Hindi', 'Hindi'),
        ('English', 'English'),
        ('Tamil', 'Tamil'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField()
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES)
    language = models.CharField(max_length=20, choices=LANGUAGE_CHOICES)
    duration = models.IntegerField()
    release_date = models.DateField()

    def __str__(self):
        return self.title
