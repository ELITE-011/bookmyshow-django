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