from datetime import datetime, timezone


class UserModel:
    """User document schema for MongoDB."""
    collection_name = 'users'

    @staticmethod
    def create_schema(name, email, hashed_password):
        return {
            'name': name,
            'email': email,
            'password': hashed_password,
            'created_at': datetime.now(timezone.utc),
            'updated_at': datetime.now(timezone.utc),
        }
