
from channels.routing import URLRouter
from django.urls import re_path
from share.consumers import ShareConsumer

websocket_urlpatterns = [
    re_path(r'ws/share/(?P<group>\S+)/$', ShareConsumer.as_asgi()),
]