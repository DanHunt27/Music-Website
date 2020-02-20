from django.shortcuts import render
from django.http import HttpResponseNotFound
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.safestring import mark_safe
from django.db.models import Q
from .models import Chat
import json
import re

@login_required
def index(request):
    chats = Chat.objects.filter(Q(user1=request.user)|Q(user2=request.user))
    return render(request, 'chat/chat-index.html', {'chats': chats})

@login_required
def room(request, room_name):
    try:
        user1 = re.search('([a-zA-Z\d\-]+)_[a-zA-Z\d\-]+', room_name).group(1)
    except:
        user1 = ''

    try:
        user2 = re.search('_([a-zA-Z\d\-]+)', room_name).group(1)
    except:
        user2 = ''

    if not (User.objects.filter(username=user1).exists() and User.objects.filter(username=user2).exists()):
        return HttpResponseNotFound("One of those users don't exist")

    if user1 == request.user.username or user2 == request.user.username:
        if user1 == request.user.username:
            receiver_img = User.objects.get(username=user2).profile.image
            receiver_name = user2
        else:
            receiver_img = User.objects.get(username=user1).profile.image
            receiver_name = user1

        return render(request, 'chat/room.html', {
            'room_name_json': mark_safe(json.dumps(room_name)),
            'room_name': room_name,
            'username': mark_safe(json.dumps(request.user.username)),
            'receiver': mark_safe(json.dumps(receiver_name)),
            'receiver_name': receiver_name,
            'receiver_image': receiver_img,
            'chats': Chat.objects.filter(Q(user1=request.user)|Q(user2=request.user))
        })
    else:
        return HttpResponseNotFound("Incorrect User")
