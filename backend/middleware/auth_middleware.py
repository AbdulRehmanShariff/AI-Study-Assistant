from functools import wraps
from flask import request
from services.auth_service import AuthService
from utils.response import error_response


def require_auth(f):
    """Decorator to protect routes — verifies JWT and attaches user_id to request."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization', '')

        if not auth_header:
            return error_response('Authorization header missing', status=401)

        if not auth_header.startswith('Bearer '):
            return error_response('Invalid authorization format. Use: Bearer <token>', status=401)

        token = auth_header.split(' ', 1)[1].strip()

        if not token:
            return error_response('Token missing', status=401)

        try:
            user_id = AuthService.verify_token(token)
            # Attach user_id directly to the request object
            request.user_id = user_id
        except ValueError as e:
            return error_response(str(e), status=401)
        except Exception:
            return error_response('Authentication failed', status=401)

        return f(*args, **kwargs)
    return decorated
