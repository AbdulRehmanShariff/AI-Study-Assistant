from flask import request
from services.summary_service import SummaryService
from middleware.auth_middleware import require_auth
from utils.response import success_response, error_response


class SummaryController:
    """Handles summary generation requests."""

    @staticmethod
    @require_auth
    def generate():
        """POST /api/summaries/generate — Generate or retrieve a summary."""
        data = request.get_json()
        if not data:
            return error_response('Request body must be JSON', status=400)

        document_id = data.get('document_id')
        style       = data.get('style', 'concise')

        if not document_id:
            return error_response('document_id is required', status=400)

        user_id = request.user_id

        try:
            summary = SummaryService.generate_summary(user_id, document_id, style)
            return success_response(
                'Summary generated successfully',
                data={'summary': summary, 'style': style, 'document_id': document_id}
            )
        except ValueError as e:
            return error_response(str(e), status=400)
        except RuntimeError as e:
            return error_response(str(e), status=502)
        except Exception as e:
            return error_response('Failed to generate summary', error=str(e), status=500)
