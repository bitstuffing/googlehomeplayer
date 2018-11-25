from django.db import models


class Track(models.Model):
    name = models.CharField(max_length=30)
    url = models.CharField(max_length=1024)

class Playist(models.Model):
    name = models.CharField(max_length=30)
    models.ForeignKey(Track, on_delete=models.CASCADE)
