from functools import wraps
from flask import request
from utils.response import error_response


def validate_json(*required_fields):
    """Decorator to validate required JSON fields in request body."""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            data = request.get_json()
            if not data:
                return error_response('Request body must be JSON', status=400)

            missing = [field for field in required_fields if field not in data]
            if missing:
                return error_response(
                    f'Missing required fields: {", ".join(missing)}',
                    status=400
                )
            return f(*args, **kwargs)
        return decorated
    return decorator


def validate_file(allowed_extensions=None, max_size_mb=50):
    """Decorator to validate uploaded files."""
    if allowed_extensions is None:
        allowed_extensions = {'pdf', 'txt'}

    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'file' not in request.files:
                return error_response('No file provided', status=400)

            file = request.files['file']
            if file.filename == '':
                return error_response('No file selected', status=400)

            # Check extension
            ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
            if ext not in allowed_extensions:
                return error_response(
                    f'File type not allowed. Allowed: {", ".join(allowed_extensions)}',
                    status=400
                )

            return f(*args, **kwargs)
        return decorated
    return decorator
