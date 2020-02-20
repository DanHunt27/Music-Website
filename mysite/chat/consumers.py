from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models import Message, Chat
from django.contrib.auth.models import User
import json
from django.shortcuts import get_object_or_404
import re

class ChatConsumer(WebsocketConsumer):

    def fetch_messages(self, data):
        messages = Message.last_20_messages(data['room'])
        content = {
            'command': 'messages',
            'messages': self.messages_to_json(messages)
        }
        self.send_message(content)

    def new_message(self, data):
        author = data['from']
        receiver = data['receiver']
        room = data['room_name']
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
        author_user = User.objects.filter(username=author)[0]
        receiver_user = User.objects.filter(username=receiver)[0]
        if Chat.objects.filter(user1=user1, user2=user2).exists():
            chat = Chat.objects.get(user1=user1, user2=user2)
        elif Chat.objects.filter(user1=user2, user2=user1).exists():
            chat = self.room_name = Chat.objects.get(user1=user2, user2=user1)
        message = Message.objects.create(author=author_user, receiver=receiver_user, content=data['message'], chat=chat)
        content = {
            'command': 'new_message',
            'message': self.message_to_json(message)
        }
        return self.send_chat_message(content)

    def messages_to_json(self, messages):
        result = []
        for message in messages:
            result.append(self.message_to_json(message))
        return result

    def message_to_json(self, message):
        return {
            'author': message.author.username,
            'content': message.content,
            'timestamp': str(message.timestamp)
        }

    commands = {
        'fetch_messages' : fetch_messages,
        'new_message' : new_message
    }

    def connect(self):
        room = self.scope['url_route']['kwargs']['room_name']
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
        if Chat.objects.filter(user1=user1, user2=user2).exists():
            self.room_name = Chat.objects.get(user1=user1, user2=user2).room_name
        elif Chat.objects.filter(user1=user2, user2=user1).exists():
            self.room_name = Chat.objects.get(user1=user2, user2=user1).room_name
        else:
            room_name = user1.username + '_' + user2.username
            chat = Chat(user1=user1, user2=user2, room_name=room_name)
            chat.save()
            self.room_name = room_name

        self.room_group_name = 'chat_%s' % self.room_name
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)

    def send_chat_message(self, message):
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    def send_message(self, message):
        self.send(text_data=json.dumps(message))

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        # Send message to WebSocket
        self.send(text_data=json.dumps(message))
