import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application
from common.middleware.socketAuth import SocketAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm.settings')
django_asgi_app = get_asgi_application()

import chat.routing
import notification.routing

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            SocketAuthMiddleware(
                URLRouter(
                    chat.routing.websocket_urlpatterns +
                    notification.routing.websocket_urlpatterns
                )
            )
        ),
    }
)