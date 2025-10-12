

import os
from channels.routing import URLRouter,ProtocolTypeRouter
import django
from channels.auth import AuthMiddleware
from auth_api import routing

django.setup()

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

application = ProtocolTypeRouter(
    {
        'http' : get_asgi_application(),
        'websocket' : AuthMiddleware(
            URLRouter(
                routing.ws_pattern
            )
        )
    }
)
