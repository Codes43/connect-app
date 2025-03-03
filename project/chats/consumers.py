import base64
from contextvars import Context
from django.db.models.functions import Coalesce
import json
from multiprocessing import Value, context
from django.core.files.base import ContentFile
from django.db.models import Q, Exists, OuterRef
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from flask import request
from itsdangerous import Serializer
from .serializers import *
from .models import Connection, User, Message


class ChatsConsumer(WebsocketConsumer):

    def connect(self):
        user = self.scope['user']
        print(user, user.is_authenticated)

        if not user.is_authenticated:
            return

            # Save username to use as a group name for this user
        self.username = user.username
        # Join this user to a group with their username
        async_to_sync(self.channel_layer.group_add)(
            self.username, self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # Leave room/group
        async_to_sync(self.channel_layer.group_discard)(
            self.username, self.channel_name
        )

    # -----------------------
    #    Handle requests
    # -----------------------

    def receive(self, text_data):
        # Receive message from websocket
        data = json.loads(text_data)
        data_source = data.get('source')

        # Pretty print  python dict

        print('receive', json.dumps(data, indent=2))

        if data_source == 'search':
            self.receive_search(data)
        elif data_source == 'friend.list':
            self.receiveFriendsList(data)
        elif data_source == 'request.accept':
            self.receiveAcceptRequest(data)
        # Get request list
        elif data_source == 'request.list':
            self.receiveRequest_list(data)
        elif data_source == 'message.send':
            self.recieve_message_send(data)
           # handle message request
        elif data_source == 'message.list':
            self.recieve_message_list(data)
           # when user is typing
        elif data_source == 'message.type':
            self.recieve_message_type(data)

           # friend requsets
        elif data_source == 'request.follow':
            self.receiveRequest_follow(data)
            # upload user profile
        elif data_source == 'thumbnail':
            self.receive_thumbnail(data)

    def recieve_message_type(self, data):
        user = self.scope['user']
        recipient_username = data.get('username')
        data = {
            'username': user.username
        }
        self.send_group(recipient_username, 'message.type', data)

    def receiveFriendsList(self, data):
        user = self.scope['user']

        # latest/new message subquery
        latest_message = Message.objects.filter(
            connection=OuterRef('id')
        ).order_by('-created')[:1]

        # connections
        connections = Connection.objects.filter(
            Q(sender=user) | Q(receiver=user),
            accepted=True
        ).annotate(
            latest_text=latest_message.values('text'),
            latest_created=latest_message.values('created')
        ).order_by(
            Coalesce('latest_created', 'updated').desc()
        )

        serialized = FriendsSerializer(
            connections, context={'user': user}, many=True)
        self.send_group(user.username, 'friend.list', serialized.data)

    def receiveAcceptRequest(self, data):
        username = data.get('username')
        # try fetching the connection object
        try:
            connection = Connection.objects.get(
                sender__username=username,
                receiver=self.scope['user']
            )
        except Connection.DoesNotExist:
            print('Error: connection doesn,t exist')
            return

        # updating the connnection
        connection.accepted = True
        connection.save()

        # serialised data
        serialized = RequestSerializer(connection)
        # send the accepet to sender
        self.send_group(
            connection.sender.username, 'request.accept', serialized.data
        )
        self.send_group(
            connection.receiver.username, 'request.accept', serialized.data
        )

    def receiveRequest_list(self, data):
        user = self.scope['user']
        connections = Connection.objects.filter(
            receiver=user,
            accepted=False
        )

        serialized = RequestSerializer(connections, many=True)

        self.send_group(user.username, 'request.list', serialized.data)

    def recieve_message_list(self, data):
        user = self.scope['user']
        connectionId = data.get('connectionId')
        page = data.get('page')

        try:
            connection = Connection.objects.get(id=connectionId)
        except Connection.DoesNotExist:
            print('connection doesn,t exist')
            return

         # get messsages

        messages = Message.objects.filter(
            connection=connection
        ).order_by('-created')
        # get serialised messsages
        serialized_messages = MessageSerializer(
            messages,
            context={
                'user': user,
            },
            many=True
        )
        # reciever or reciepient
        recipient = connection.sender
        if connection.sender == user:
            recipient = connection.receiver

        # serialised friend
        serialized_friend = UserSerializer(recipient)
        data = {
            'messages': serialized_messages.data,
            'friend': serialized_friend.data
        }
        # send back the message to the requestor
        self.send_group(user.username, 'message.list', data)

    def recieve_message_send(self, data):
        user = self.scope['user']
        connectionId = data.get('connectionId')
        message_text = data.get('message')
        try:
            connection = Connection.objects.get(id=connectionId)
        except Connection.DoesNotExist:
            print('Error: couldnt find connection')
            return

        message = Message.objects.create(
            connection=connection,
            user=user,
            text=message_text
        )

        # Get recipient friend
        recipient = connection.sender
        if connection.sender == user:
            recipient = connection.receiver

            # Send new message back to sender
        serialized_message = MessageSerializer(
            message,
            context={
                'user': user
            }
        )
        serialized_friend = UserSerializer(recipient)
        data = {
            'message': serialized_message.data,
            'friend': serialized_friend.data
        }
        self.send_group(user.username, 'message.send', data)

        # Send new message to receiver
        serialized_message = MessageSerializer(
            message,
            context={
                'user': recipient
            }
        )
        serialized_friend = UserSerializer(user)
        data = {
            'message': serialized_message.data,
            'friend': serialized_friend.data
        }
        self.send_group(recipient.username, 'message.send', data)

    def receiveRequest_follow(self, data):
        username = data.get('username')

        # recieve follower
        try:
            receiver = User.objects.get(username=username)
        except User.DoesNotExist:

            print('User: Doesn,t Exist')
        # create connection
        connection, _ = Connection.objects.get_or_create(
            sender=self.scope['user'],
            receiver=receiver
        )

        serialized = RequestSerializer(connection)

        # send back to our selves
        self.send_group(connection.sender.username,
                        'request.follow', serialized.data)
        # send to other or recieve
        self.send_group(connection.receiver.username,
                        'request.follow', serialized.data)

    def receive_search(self, data):
        query = data.get('query')

        users = User.objects.filter(
            Q(username__istartswith=query) |
            Q(first_name__istartswith=query) |
            Q(last_name__istartswith=query)
        ).exclude(
            username=self.username).annotate(
            Pending_them=Exists(
                Connection.objects.filter(
                    sender=self.scope['user'],
                    receiver=OuterRef('id'),
                    accepted=False
                ),
            ),
            Pending_me=Exists(
                Connection.objects.filter(
                    sender=OuterRef('id'),
                    receiver=self.scope['user'],
                    accepted=False
                ),
            ),
            connected=Exists(
                Connection.objects.filter(
                    Q(sender=self.scope['user'], receiver=OuterRef('id')) |
                    Q(receiver=self.scope['user'], sender=OuterRef('id')),
                    accepted=True
                ),
            )

        )

        serialized = SearchSerializer(users, many=True)
        self.send_group(self.username, 'search', serialized.data)

    def receive_thumbnail(self, data):
        user = self.scope['user']
        # Convert base64 data  to django content file
        image_str = data.get('base64')
        image = ContentFile(base64.b64decode(image_str))  # type: ignore
        # Update thumbnail field
        filename = data.get('filename')
        user.thumbnail.save(filename, image, save=True)
        # Serialize user
        serialized = UserSerializer(user)
        # Send updated user data including new thumbnail
        self.send_group(self.username, 'thumbnail', serialized.data)

    #   calls broadcast to client helpers

    def send_group(self, group, source, data):
        response = {
            'type': 'broadcast_group',
            'source': source,
            'data': data
        }
        async_to_sync(self.channel_layer.group_send)(
            group, response
        )

    def broadcast_group(self, data):
        '''
        data:
                - type: 'broadcast_group'
                - source: where it originated from
                - data: what ever you want to send as a dict
        '''
        data.pop('type')
        '''
                return data:
                        - source: where it originated from
                        - data: what ever you want to send as a dict
                '''
        self.send(text_data=json.dumps(data))
