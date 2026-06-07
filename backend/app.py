import os
import sys

from flask import Flask, jsonify
from flask_cors import CORS

from config.settings import Config
from config.database import Database
from routes import register_routes
from utils.response import error_response


def create_app():
    """Application factory — creates and configures the Flask app."""

    app = Flask(__name__)

    # -----------------------------------
    # 1. Load Configuration
    # -----------------------------------
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH

    # -----------------------------------
    # 2. Enable CORS
    # -----------------------------------
    CORS(app, resources={
        r'/api/*': {
            'origins': [Config.FRONTEND_URL],
            'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
            'allow_headers': ['Content-Type', 'Authorization'],
            'supports_credentials': True,
        }
    })

    # -----------------------------------
    # 3. Create Required Directories
    # -----------------------------------
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(Config.VECTOR_STORE_PATH, exist_ok=True)

    # -----------------------------------
    # 4. Initialize Database
    # -----------------------------------
    with app.app_context():
        db = Database.connect()
        if db is not None:
            Database.create_indexes()
        else:
            print('[WARNING] Running without database connection.')
            print('   Make sure MongoDB is running and MONGO_URI is correct in .env')

    # -----------------------------------
    # 5. Pre-warm Embedding Model (background)
    # -----------------------------------
    def _warm_up_embedder():
        try:
            from utils.embedder import Embedder
            Embedder.get_model()
        except Exception as e:
            print(f'[WARNING] Embedder warm-up failed: {e}')

    import threading
    threading.Thread(target=_warm_up_embedder, daemon=True).start()

    # -----------------------------------
    # 6. Register Route Blueprints
    # -----------------------------------
    register_routes(app)

    # -----------------------------------
    # 6. Health Check Endpoint
    # -----------------------------------
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint to verify server is running."""
        db_status = 'connected' if Database.get_db() is not None else 'disconnected'

        return jsonify({
            'success': True,
            'message': 'AI Study Assistant API is running',
            'data': {
                'status': 'healthy',
                'database': db_status,
                'environment': Config.FLASK_ENV,
            }
        }), 200

    # -----------------------------------
    # 7. Error Handlers
    # -----------------------------------
    @app.errorhandler(400)
    def bad_request(error):
        return error_response('Bad request', status=400)

    @app.errorhandler(401)
    def unauthorized(error):
        return error_response('Unauthorized', status=401)

    @app.errorhandler(403)
    def forbidden(error):
        return error_response('Forbidden', status=403)

    @app.errorhandler(404)
    def not_found(error):
        return error_response('Resource not found', status=404)

    @app.errorhandler(413)
    def file_too_large(error):
        return error_response(
            f'File too large. Maximum size is {Config.MAX_FILE_SIZE_MB}MB',
            status=413
        )

    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return error_response('Rate limit exceeded. Try again later.', status=429)

    @app.errorhandler(500)
    def internal_error(error):
        return error_response('Internal server error', status=500)

    return app


# -----------------------------------
# Entry Point
# -----------------------------------
if __name__ == '__main__':
    app = create_app()
    print()
    print('AI Study Assistant API')
    print('===============================')
    print(f'  Environment : {Config.FLASK_ENV}')
    print(f'  Frontend URL: {Config.FRONTEND_URL}')
    print(f'  Upload dir  : {Config.UPLOAD_FOLDER}')
    print(f'  Vector store: {Config.VECTOR_STORE_PATH}')
    print(f'  Running on  : http://localhost:5000')
    print()
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=Config.FLASK_DEBUG,
        use_reloader=False,
    )
