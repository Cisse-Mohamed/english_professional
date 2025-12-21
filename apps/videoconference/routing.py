from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/video/regular/(?P<session_slug>[\w-]+)/(?:breakout/(?P<breakout_slug>[\w-]+)/)?$', consumers.VideoCallConsumer.as_asgi(), {'session_type': 'regular'}),
    re_path(r'ws/video/instant/(?P<session_slug>[\w-]+)/$', consumers.VideoCallConsumer.as_asgi(), {'session_type': 'instant'}),
]
