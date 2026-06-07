from flask import request
from services.auth_service import AuthService
from middleware.auth_middleware import require_auth
from utils.response import success_response, error_response


class AuthController:
    """Handles authentication request/response logic."""

    @staticmethod
    def register():
        """POST /api/auth/register"""
        data = request.get_json()
        if not data:
            return error_response('Request body must be JSON', status=400)

        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')

        try:
            user, token = AuthService.register(name, email, password)
            return success_response(
                'Account created successfully',
                data={'user': user, 'token': token},
                status=201
            )
        except ValueError as e:
            return error_response(str(e), status=400)
        except Exception as e:
            return error_response('Registration failed', error=str(e), status=500)

    @staticmethod
    def login():
        """POST /api/auth/login"""
        data = request.get_json()
        if not data:
            return error_response('Request body must be JSON', status=400)

        email = data.get('email', '').strip()
        password = data.get('password', '')

        try:
            user, token = AuthService.login(email, password)
            return success_response(
                'Login successful',
                data={'user': user, 'token': token},
                status=200
            )
        except ValueError as e:
            return error_response(str(e), status=401)
        except Exception as e:
            return error_response('Login failed', error=str(e), status=500)

    @staticmethod
    @require_auth
    def get_me():
        """GET /api/auth/me"""
        user_id = request.user_id
        try:
            user = AuthService.get_me(user_id)
            return success_response('User retrieved', data={'user': user})
        except ValueError as e:
            return error_response(str(e), status=404)
        except Exception as e:
            return error_response('Failed to get user', error=str(e), status=500)

    @staticmethod
    @require_auth
    def update_profile():
        """PUT /api/auth/profile"""
        data = request.get_json()
        if not data:
            return error_response('Request body must be JSON', status=400)

        user_id = request.user_id
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()

        try:
            user = AuthService.update_profile(user_id, name, email)
            return success_response('Profile updated', data={'user': user})
        except ValueError as e:
            return error_response(str(e), status=400)
        except Exception as e:
            return error_response('Failed to update profile', error=str(e), status=500)

    @staticmethod
    @require_auth
    def change_password():
        """PUT /api/auth/password"""
        data = request.get_json()
        if not data:
            return error_response('Request body must be JSON', status=400)

        user_id = request.user_id
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')

        try:
            AuthService.change_password(user_id, current_password, new_password)
            return success_response('Password changed successfully')
        except ValueError as e:
            return error_response(str(e), status=400)
        except Exception as e:
            return error_response('Failed to change password', error=str(e), status=500)

    @staticmethod
    @require_auth
    def delete_account():
        """DELETE /api/auth/account"""
        user_id = request.user_id
        try:
            AuthService.delete_account(user_id)
            return success_response('Account deleted successfully')
        except Exception as e:
            return error_response('Failed to delete account', error=str(e), status=500)
