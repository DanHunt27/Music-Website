from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse

class Post(models.Model):
    artist_name = models.CharField(max_length=100)
    song_name = models.CharField(max_length=100)
    description = models.TextField(max_length=280, blank=True, default='')
    link = models.URLField(max_length=1000)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.artist_name + " - " + self.song_name

    def get_absolute_url(self):
        return reverse('index')

class Comment(models.Model):
    post = models.ForeignKey('main.Post', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.text
