"""
ASGI config for core project.

It exposes the ASGI callable as a module-level variable named ``application``.

Pour le support WebSocket, ce fichier est étendu avec Channels.
"""

import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Default ASGI application pour HTTP
application = get_asgi_application()

# WebSocket routing (si Channels installé)
try:
    from channels.routing import ProtocolTypeRouter, URLRouter
    from channels.auth import AuthMiddlewareStack
    from channels.security.websocket import AllowedHostsOriginValidator
    from channels.middleware import BaseMiddleware
    from channels.db import database_sync_to_async
    from django.contrib.auth.models import AnonymousUser, User
    from rest_framework_simplejwt.tokens import AccessToken
    from urllib.parse import parse_qs
    from chat.routing import websocket_urlpatterns
    
    @database_sync_to_async
    def get_user_from_token(token_string):
        try:
            access_token = AccessToken(token_string)
            user_id = access_token['user_id']
            return User.objects.get(id=user_id)
        except Exception:
            return AnonymousUser()

    class JWTAuthMiddleware(BaseMiddleware):
        async def __call__(self, scope, receive, send):
            query_string = scope.get('query_string', b'').decode()
            query_params = parse_qs(query_string)
            token = query_params.get('token', [None])[0]
            if token:
                scope['user'] = await get_user_from_token(token)
            else:
                scope['user'] = AnonymousUser()
            return await super().__call__(scope, receive, send)

    # Application ASGI complète avec WebSocket
    application = ProtocolTypeRouter({
        "http": get_asgi_application(),
        "websocket": AllowedHostsOriginValidator(
            JWTAuthMiddleware(
                URLRouter(websocket_urlpatterns)
            )
        ),
    })
except ImportError:
    # Fallback si Channels non installé
    pass
except Exception as e:
    # Logging silencieux pour le développement
    print(f"Warning: WebSocket non disponible ({e})")
