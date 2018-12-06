from django.db import models

class Playlist(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Track(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=40)
    url = models.CharField(max_length=1024)
    original_url = models.CharField(max_length=1024)
    duration = models.FloatField(default=0.0,null=True)
    type = models.CharField(max_length=5) #audio, video, page
    playlist = models.ForeignKey(Playlist,on_delete=models.CASCADE)
    description = models.TextField(default="UNKNOWN",null=True)
    thumbnail = models.CharField(max_length=1024,null=True,default="UNKNOWN")
    creator = models.CharField(max_length=40,null=True,default="UNKNOWN")

class CurrentPlaylist(models.Model):
    id = models.AutoField(primary_key=True)
    device = models.IntegerField(default=0,null=True)
    playlist = models.ForeignKey(Playlist,on_delete=models.CASCADE)
    random = models.BooleanField(default=False)
    current_track = models.ForeignKey(Track,on_delete=models.CASCADE,null=True)

class Device(models.Model):
    id = models.AutoField(primary_key=True)
    ip_address = models.CharField(max_length=15)
    port = models.CharField(max_length=5)
    friendly_name = models.CharField(max_length=60)
    model_name = models.CharField(max_length=20)
    uuid = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Status(models.Model):
    id = models.AutoField(primary_key=True)
    duration = models.FloatField(default=0.0,null=True)
    current = models.FloatField(default=0.0,null=True)
    state = models.CharField(max_length=20,default="UNKNOWN",null=True)
    volume = models.FloatField(default=0.0,null=True)
    content = models.TextField(default="UNKNOWN",null=True)
    app = models.CharField(max_length=20,default="UNKNNOWN",null=True)
    updated = models.DateTimeField(auto_now=True)
