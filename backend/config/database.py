from pymongo import MongoClient
from config.settings import Config


class Database:
    """MongoDB connection manager."""

    _client = None
    _db = None

    @classmethod
    def connect(cls):
        """Establish connection to MongoDB."""
        if cls._client is None:
            try:
                cls._client = MongoClient(
                    Config.MONGO_URI,
                    serverSelectionTimeoutMS=2000,  # Fail fast: 2s timeout
                    connectTimeoutMS=2000,
                    socketTimeoutMS=2000,
                )
                # Extract database name from URI, or use default
                db_name = Config.MONGO_URI.rsplit('/', 1)[-1].split('?')[0]
                if not db_name:
                    db_name = 'ai_study_assistant'
                cls._db = cls._client[db_name]
                # Test connection
                cls._client.admin.command('ping')
                print(f'[OK] Connected to MongoDB: {db_name}')
            except Exception as e:
                print(f'[ERROR] MongoDB connection failed: {e}')
                cls._client = None
                cls._db = None
        return cls._db

    @classmethod
    def get_db(cls):
        """Get the database instance."""
        if cls._db is None:
            return cls.connect()
        return cls._db

    @classmethod
    def get_collection(cls, collection_name):
        """Get a specific collection."""
        db = cls.get_db()
        if db is not None:
            return db[collection_name]
        return None

    @classmethod
    def close(cls):
        """Close the MongoDB connection."""
        if cls._client:
            cls._client.close()
            cls._client = None
            cls._db = None
            print('[INFO] MongoDB connection closed.')

    @classmethod
    def create_indexes(cls):
        """Create database indexes for optimal performance."""
        db = cls.get_db()
        if db is None:
            print('[ERROR] Cannot create indexes: No database connection')
            return

        try:
            # Users: unique email index
            db.users.create_index('email', unique=True)

            # Documents: user_id index
            db.documents.create_index('user_id')

            # Chats: compound index for user_id + session_id
            db.chats.create_index([('user_id', 1), ('session_id', 1)])

            # Flashcards: user_id index
            db.flashcards.create_index('user_id')

            # Quizzes: user_id index
            db.quizzes.create_index('user_id')

            # Quiz Results: compound index for user_id + quiz_id
            db.quiz_results.create_index([('user_id', 1), ('quiz_id', 1)])

            # Chunks: document_id and compound index for retrieval
            db.chunks.create_index('document_id')
            db.chunks.create_index([('document_id', 1), ('chunk_index', 1)])
            db.chunks.create_index('user_id')

            print('[OK] Database indexes created successfully')
        except Exception as e:
            print(f'[ERROR] Error creating indexes: {e}')
