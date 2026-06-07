from flask import request
from services.quiz_service import QuizService
from middleware.auth_middleware import require_auth
from utils.response import success_response, error_response


class QuizController:
    """Handles quiz generation and retrieval requests."""

    @staticmethod
    @require_auth
    def generate():
        """POST /api/quiz/generate — Generate a quiz for a document."""
        data = request.get_json()
        if not data:
            return error_response('Request body must be JSON', status=400)

        document_id = data.get('document_id')
        count = data.get('count', 5)

        if not document_id:
            return error_response('document_id is required', status=400)

        user_id = request.user_id

        try:
            quiz = QuizService.generate_quiz(user_id, document_id, count)
            return success_response('Quiz generated successfully', data={'quiz': quiz})
        except ValueError as e:
            return error_response(str(e), status=400)
        except RuntimeError as e:
            return error_response(str(e), status=502)
        except Exception as e:
            return error_response('Failed to generate quiz', error=str(e), status=500)

    @staticmethod
    @require_auth
    def get_by_document(document_id):
        """GET /api/quiz/<document_id> — Fetch quiz for a document."""
        user_id = request.user_id
        try:
            quiz = QuizService.get_quiz(user_id, document_id)
            if not quiz:
                return error_response('Quiz not found for this document', status=404)
            return success_response('Quiz retrieved', data={'quiz': quiz})
        except Exception as e:
            return error_response('Failed to retrieve quiz', error=str(e), status=500)
