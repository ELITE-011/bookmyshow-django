from django.db import models

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

    def __str__(self):
        return self.title