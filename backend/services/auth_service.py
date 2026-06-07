import bcrypt
import jwt
from datetime import datetime, timedelta, timezone
from bson import ObjectId

from config.settings import Config
from config.database import Database
from models.user_model import UserModel


class AuthService:
    """Business logic for authentication."""

    @staticmethod
    def _get_collection():
        return Database.get_collection(UserModel.collection_name)

    @staticmethod
    def _serialize_user(user):
        """Convert MongoDB user doc to safe dict (no password)."""
        return {
            'id': str(user['_id']),
            'name': user['name'],
            'email': user['email'],
            'created_at': user['created_at'].isoformat(),
        }

    @staticmethod
    def _generate_token(user_id):
        """Generate a JWT token for the given user ID."""
        expiry = datetime.now(timezone.utc) + timedelta(
            hours=Config.JWT_EXPIRATION_HOURS
        )
        payload = {
            'user_id': str(user_id),
            'exp': expiry,
            'iat': datetime.now(timezone.utc),
        }
        return jwt.encode(payload, Config.JWT_SECRET_KEY, algorithm='HS256')

    @staticmethod
    def register(name, email, password):
        """Register a new user.

        Returns:
            (user_dict, token) on success
        Raises:
            ValueError: if email already exists or validation fails
        """
        col = AuthService._get_collection()

        # Validate inputs
        if not name or not name.strip():
            raise ValueError('Name is required')
        if not email or not email.strip():
            raise ValueError('Email is required')
        if not password or len(password) < 6:
            raise ValueError('Password must be at least 6 characters')

        email = email.lower().strip()

        # Check duplicate email
        if col.find_one({'email': email}):
            raise ValueError('An account with this email already exists')

        # Hash password
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12))

        # Create user document
        user_doc = UserModel.create_schema(
            name=name.strip(),
            email=email,
            hashed_password=hashed.decode('utf-8'),
        )

        result = col.insert_one(user_doc)
        user_doc['_id'] = result.inserted_id

        token = AuthService._generate_token(result.inserted_id)
        return AuthService._serialize_user(user_doc), token

    @staticmethod
    def login(email, password):
        """Login user with email and password.

        Returns:
            (user_dict, token) on success
        Raises:
            ValueError: if credentials are invalid
        """
        col = AuthService._get_collection()

        if not email or not password:
            raise ValueError('Email and password are required')

        email = email.lower().strip()
        user = col.find_one({'email': email})

        if not user:
            raise ValueError('Invalid email or password')

        # Verify password
        if not bcrypt.checkpw(
            password.encode('utf-8'),
            user['password'].encode('utf-8')
        ):
            raise ValueError('Invalid email or password')

        token = AuthService._generate_token(user['_id'])
        return AuthService._serialize_user(user), token

    @staticmethod
    def get_me(user_id):
        """Get user by ID.

        Returns:
            user_dict on success
        Raises:
            ValueError: if user not found
        """
        col = AuthService._get_collection()

        try:
            user = col.find_one({'_id': ObjectId(user_id)})
        except Exception:
            raise ValueError('Invalid user ID')

        if not user:
            raise ValueError('User not found')

        return AuthService._serialize_user(user)

    @staticmethod
    def update_profile(user_id, name, email):
        """Update user name and email.

        Returns:
            updated user_dict
        Raises:
            ValueError: on validation error or duplicate email
        """
        col = AuthService._get_collection()

        if not name or not name.strip():
            raise ValueError('Name is required')
        if not email or not email.strip():
            raise ValueError('Email is required')

        email = email.lower().strip()

        # Check if email is taken by another user
        existing = col.find_one({'email': email})
        if existing and str(existing['_id']) != user_id:
            raise ValueError('Email already in use by another account')

        col.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {
                'name': name.strip(),
                'email': email,
                'updated_at': datetime.now(timezone.utc),
            }}
        )

        return AuthService.get_me(user_id)

    @staticmethod
    def change_password(user_id, current_password, new_password):
        """Change user password.

        Raises:
            ValueError: if current password is wrong or new password too short
        """
        col = AuthService._get_collection()

        if not new_password or len(new_password) < 6:
            raise ValueError('New password must be at least 6 characters')

        user = col.find_one({'_id': ObjectId(user_id)})
        if not user:
            raise ValueError('User not found')

        # Verify current password
        if not bcrypt.checkpw(
            current_password.encode('utf-8'),
            user['password'].encode('utf-8')
        ):
            raise ValueError('Current password is incorrect')

        # Hash new password
        new_hashed = bcrypt.hashpw(
            new_password.encode('utf-8'), bcrypt.gensalt(12)
        )

        col.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {
                'password': new_hashed.decode('utf-8'),
                'updated_at': datetime.now(timezone.utc),
            }}
        )

    @staticmethod
    def verify_token(token):
        """Verify a JWT token and return the user_id.

        Returns:
            user_id string on success
        Raises:
            ValueError: if token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                Config.JWT_SECRET_KEY,
                algorithms=['HS256']
            )
            return payload['user_id']
        except jwt.ExpiredSignatureError:
            raise ValueError('Token has expired. Please log in again.')
        except jwt.InvalidTokenError:
            raise ValueError('Invalid token. Please log in again.')

    @staticmethod
    def delete_account(user_id):
        """Delete user account and all associated data."""
        from models.document_model import DocumentModel
        from models.chat_model import ChatMessageModel
        from models.quiz_model import QuizModel
        
        db = Database.get_db()
        db[DocumentModel.collection_name].delete_many({'user_id': user_id})
        db[ChatMessageModel.collection_name].delete_many({'user_id': user_id})
        db[QuizModel.collection_name].delete_many({'user_id': user_id})
        db['flashcards'].delete_many({'user_id': user_id})
        
        col = AuthService._get_collection()
        col.delete_one({'_id': ObjectId(user_id)})
