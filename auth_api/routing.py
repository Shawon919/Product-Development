from django.urls import re_path
from .comsumer import MyAsyncWebSocketConsumer


ws_pattern = [
    re_path(r'ws/chat/(?P<receiver_id>\w+)/$',MyAsyncWebSocketConsumer.as_asgi())
]
