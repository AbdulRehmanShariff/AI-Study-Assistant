from flask import Blueprint

def register_routes(app):
    """Register all route blueprints with the Flask app."""
    from .auth_routes import auth_bp
    from .document_routes import document_bp
    from .chat_routes import chat_bp
    from .summary_routes import summary_bp
    from .flashcard_routes import flashcard_bp
    from .quiz_routes import quiz_bp
    from .dashboard_routes import dashboard_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(document_bp, url_prefix='/api/documents')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    app.register_blueprint(summary_bp, url_prefix='/api/summaries')
    app.register_blueprint(flashcard_bp, url_prefix='/api/flashcards')
    app.register_blueprint(quiz_bp, url_prefix='/api/quiz')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
