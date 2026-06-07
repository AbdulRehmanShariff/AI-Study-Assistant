from flask import request
from services.rag_service import RAGService
from services.chat_service import ChatService
from middleware.auth_middleware import require_auth
from utils.response import success_response, error_response
from utils.llm import GeminiLLM


class ChatController:
    """Handles chat/RAG request and response logic."""

    @staticmethod
    @require_auth
    def ask():
        """POST /api/chat/ask — Ask a question using RAG."""
        data = request.get_json()
        if not data:
            return error_response('Request body must be JSON', status=400)

        question    = data.get('question', '').strip()
        document_id = data.get('document_id')   # optional filter
        top_k       = data.get('top_k', 15)

        if not question:
            return error_response('Question is required', status=400)

        user_id = request.user_id

        try:
            result = RAGService.answer(
                user_id=user_id,
                question=question,
                document_id=document_id,
                top_k=top_k,
            )

            # Save to chat history
            try:
                ChatService.save_message(
                    user_id=user_id,
                    question=question,
                    answer=result['answer'],
                    sources=result['sources'],
                    document_id=document_id,
                )
            except Exception:
                pass  # Non-critical

            return success_response('Answer generated', data=result)

        except ValueError as e:
            return error_response(str(e), status=400)
        except RuntimeError as e:
            return error_response(str(e), status=502)
        except Exception as e:
            return error_response('Failed to generate answer', error=str(e), status=500)

    @staticmethod
    @require_auth
    def get_history():
        """GET /api/chat/history — Get recent chat messages."""
        user_id     = request.user_id
        document_id = request.args.get('document_id')
        limit       = int(request.args.get('limit', 20))

        try:
            messages = ChatService.get_history(user_id, document_id, limit)
            return success_response('History retrieved', data={'messages': messages})
        except Exception as e:
            return error_response('Failed to get history', error=str(e), status=500)

    @staticmethod
    @require_auth
    def clear_history():
        """DELETE /api/chat/history — Clear chat history."""
        user_id     = request.user_id
        document_id = request.args.get('document_id')

        try:
            count = ChatService.clear_history(user_id, document_id)
            return success_response(f'Cleared {count} messages')
        except Exception as e:
            return error_response('Failed to clear history', error=str(e), status=500)

    @staticmethod
    def status():
        """GET /api/chat/status — Check if LLM is configured."""
        return success_response('Status retrieved', data=RAGService.check_llm_status())
