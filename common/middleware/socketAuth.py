from channels.db import database_sync_to_async
from django.conf import settings
from common.models import Profile
import urllib.parse
import jwt, logging


@database_sync_to_async
def get_user(user_id, org):
    try:
        return Profile.objects.get(user_id=user_id, org=org, is_active=True)
    except:
        return None

class SocketAuthMiddleware:

    def __init__(self, app):
        # Store the ASGI application we were passed
        self.app = app
        self.logger = logging.getLogger(__name__)

    async def __call__(self, scope, receive, send):

        print("SocketAuthMiddleware")
        print(scope)
        print(receive)
        print(send)
        
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
            self.logger.error("Token or org is missing")
            return await send({"type": "websocket.close","code": 401})
        
        print(token)
        print(org)
        
        try:

            decoded = jwt.decode(token, (settings.SECRET_KEY), algorithms=[settings.JWT_ALGO])
            user_id = decoded['user_id']
            profile = await get_user(user_id, org)
            if profile:
                scope['user_id'] = profile.id
                self.logger.info("User authenticated successfully")
                return await self.app(scope, receive, send)
            else:
                self.logger.error("User not found")
                return await send({"type": "websocket.close","code": 401})
        except Exception as e:
            self.logger.error("Error decoding token")
            return await send({"type": "websocket.close","code": 500})