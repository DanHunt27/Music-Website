from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import re
from django.db.models import Q
from django.shortcuts import get_object_or_404

class Chat(models.Model):
    user1 = models.ForeignKey(User, related_name="user_1", on_delete=models.CASCADE)
    user2 = models.ForeignKey(User, related_name="user_2", on_delete=models.CASCADE)
    room_name = models.CharField(max_length=65)

    def __str__(self):
        return "{}".format(self.pk)

class Message(models.Model):
    author = models.ForeignKey(User, related_name="author_messages", on_delete=models.CASCADE)
    receiver =  models.ForeignKey(User, related_name="receiver_messages", on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(default=timezone.now)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)

    def __str__(self):
        return self.author.username

    def last_20_messages(room):
        try:
            user1_name = re.search('([a-zA-Z\d\-]+)_', room).group(1)
        except:
            user1_name = ''
        try:
            user2_name = re.search('_([a-zA-Z\d\-]+)', room).group(1)
        except:
            user2_name = ''
        user1 = get_object_or_404(User, username=user1_name)
        user2 = get_object_or_404(User, username=user2_name)
        return Message.objects.filter(Q(author=user1, receiver=user2)|Q(author=user2, receiver=user1)).order_by('timestamp')[:20]
