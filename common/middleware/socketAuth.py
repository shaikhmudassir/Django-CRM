from channels.db import database_sync_to_async
from django.conf import settings
from common.models import Profile
import urllib.parse
import jwt


@database_sync_to_async
def get_user(user_id, org):
    try:
        return Profile.objects.get(user_id=user_id, org=org, is_active=True)
    except Profile.DoesNotExist:
        return None

class SocketAuthMiddleware:

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app

    async def __call__(self, scope, receive, send):

        token = None
        org = None
        try:
            query_string = scope.get('query_string', b'').decode()
            query_params = urllib.parse.parse_qs(query_string)
            token = query_params.get('token', [None])[0]
            org = query_params.get('org', [None])[0]
        except:
            token = None
            org = None
        
        if not token or not org:
            return await send({"type": "websocket.close","code": 401})
        try:
            decoded = jwt.decode(token, (settings.SECRET_KEY), algorithms=[settings.JWT_ALGO])
            user_id = decoded['user_id']
            profile = await get_user(user_id, org)
            if profile:
                scope['user_id'] = profile.id
                return await self.app(scope, receive, send)
            else:
                return await send({"type": "websocket.close","code": 401})
        except:
            return await send({"type": "websocket.close","code": 500})