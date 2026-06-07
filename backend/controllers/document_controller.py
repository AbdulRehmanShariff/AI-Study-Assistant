from flask import request
from services.document_service import DocumentService
from middleware.auth_middleware import require_auth
from utils.response import success_response, error_response


class DocumentController:
    """Handles document management request/response logic."""

    @staticmethod
    @require_auth
    def upload():
        """POST /api/documents/upload"""
        user_id = request.user_id

        if 'file' not in request.files:
            return error_response('No file in request. Use field name: file', status=400)

        file = request.files['file']

        try:
            doc = DocumentService.upload(user_id, file)
            return success_response(
                'Document uploaded successfully',
                data={'document': doc},
                status=201
            )
        except ValueError as e:
            return error_response(str(e), status=400)
        except Exception as e:
            return error_response('Upload failed', error=str(e), status=500)

    @staticmethod
    @require_auth
    def list_documents():
        """GET /api/documents/"""
        user_id = request.user_id
        try:
            docs = DocumentService.list_documents(user_id)
            return success_response(
                'Documents retrieved',
                data={'documents': docs, 'count': len(docs)}
            )
        except Exception as e:
            return error_response('Failed to list documents', error=str(e), status=500)

    @staticmethod
    @require_auth
    def get_document(document_id):
        """GET /api/documents/<document_id>"""
        user_id = request.user_id
        try:
            doc = DocumentService.get_document(user_id, document_id)
            return success_response('Document retrieved', data={'document': doc})
        except ValueError as e:
            return error_response(str(e), status=404)
        except Exception as e:
            return error_response('Failed to get document', error=str(e), status=500)

    @staticmethod
    @require_auth
    def delete_document(document_id):
        """DELETE /api/documents/<document_id>"""
        user_id = request.user_id
        try:
            DocumentService.delete_document(user_id, document_id)
            return success_response('Document deleted successfully')
        except ValueError as e:
            return error_response(str(e), status=404)
        except Exception as e:
            return error_response('Failed to delete document', error=str(e), status=500)

    @staticmethod
    @require_auth
    def get_status(document_id):
        """GET /api/documents/<document_id>/status"""
        user_id = request.user_id
        try:
            status = DocumentService.get_status(user_id, document_id)
            return success_response('Status retrieved', data=status)
        except ValueError as e:
            return error_response(str(e), status=404)
        except Exception as e:
            return error_response('Failed to get status', error=str(e), status=500)
