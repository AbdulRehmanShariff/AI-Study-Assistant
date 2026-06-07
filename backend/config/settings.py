import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration loaded from environment variables."""

    # Flask
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')

    # MongoDB
    MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/ai_study_assistant')

    # JWT
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'dev-jwt-secret')
    JWT_EXPIRATION_HOURS = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))

    # Gemini AI
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')

    # File Upload
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '50'))
    MAX_CONTENT_LENGTH = MAX_FILE_SIZE_MB * 1024 * 1024  # Convert to bytes

    # CORS
    FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

    # RAG Configuration
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    TOP_K_RESULTS = 5
    EMBEDDING_MODEL = 'sentence-transformers/all-MiniLM-L6-v2'
    EMBEDDING_DIMENSION = 384  # Output dimension of all-MiniLM-L6-v2
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-1.5-flash')

    # Vector Store
    VECTOR_STORE_PATH = 'vector_store'
