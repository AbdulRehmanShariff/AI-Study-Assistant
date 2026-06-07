from utils.response import success_response, error_response
from config.database import Database
from middleware.auth_middleware import require_auth

class DashboardController:
    """Handles dashboard request/response logic."""

    @staticmethod
    @require_auth
    def get_stats(request):
        user_id = request.user_id
        db = Database.get_db()
        
        doc_count = db.documents.count_documents({'user_id': user_id})
        chat_count = db.chat_messages.count_documents({'user_id': user_id})
        flashcard_count = db.flashcards.count_documents({'user_id': user_id})
        quiz_count = db.quizzes.count_documents({'user_id': user_id})
        
        recent_docs_cursor = db.documents.find({'user_id': user_id}).sort('uploaded_at', -1).limit(3)
        recent_docs = []
        for d in recent_docs_cursor:
            d['_id'] = str(d['_id'])
            d['uploaded_at'] = d['uploaded_at'].isoformat()
            if d.get('processed_at'):
                d['processed_at'] = d['processed_at'].isoformat()
            recent_docs.append(d)
            
        recent_chats_cursor = db.chat_messages.find({'user_id': user_id}).sort('created_at', -1).limit(3)
        recent_chats = []
        for c in recent_chats_cursor:
            c['_id'] = str(c['_id'])
            c['created_at'] = c['created_at'].isoformat()
            recent_chats.append(c)

        return success_response('Dashboard stats', data={
            'documents': doc_count,
            'chats': chat_count,
            'flashcards': flashcard_count,
            'quizzes': quiz_count,
            'recent_documents': recent_docs,
            'recent_chats': recent_chats
        })
