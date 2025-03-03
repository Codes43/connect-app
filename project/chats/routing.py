from django.urls import path
from . import consumers

websocket_urlpatterns = {
    path('chats/', consumers.ChatsConsumer.as_asgi()),
}
