from django.db import models
from django.contrib.auth.models import User
from main.models import Post
from PIL import Image


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    #first_name
    #last_name
    total_likes = models.IntegerField(default=0)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    follows = models.ManyToManyField('self', related_name='followers', blank=True, symmetrical=False)
    likes = models.ManyToManyField(Post, related_name='liked', blank=True)

    def __str__(self):
        return f'{self.user.username} Account'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
