from flask import request
from services.flashcard_service import FlashcardService
from middleware.auth_middleware import require_auth
from utils.response import success_response, error_response


class FlashcardController:
    """Handles flashcard generation and retrieval requests."""

    @staticmethod
    @require_auth
    def generate():
        """POST /api/flashcards/generate — Generate flashcards for a document."""
        data = request.get_json()
        if not data:
            return error_response('Request body must be JSON', status=400)

        document_id = data.get('document_id')
        count = data.get('count', 10)

        if not document_id:
            return error_response('document_id is required', status=400)

        user_id = request.user_id

        try:
            deck = FlashcardService.generate_flashcards(user_id, document_id, count)
            return success_response('Flashcards generated successfully', data={'deck': deck})
        except ValueError as e:
            return error_response(str(e), status=400)
        except RuntimeError as e:
            return error_response(str(e), status=502)
        except Exception as e:
            return error_response('Failed to generate flashcards', error=str(e), status=500)

    @staticmethod
    @require_auth
    def get_by_document(document_id):
        """GET /api/flashcards/<document_id> — Fetch flashcards for a document."""
        user_id = request.user_id
        try:
            deck = FlashcardService.get_flashcards(user_id, document_id)
            if not deck:
                return error_response('Flashcards not found for this document', status=404)
            return success_response('Flashcards retrieved', data={'deck': deck})
        except Exception as e:
            return error_response('Failed to retrieve flashcards', error=str(e), status=500)
