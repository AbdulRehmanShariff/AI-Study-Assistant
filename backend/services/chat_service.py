from config.database import Database
from models.chat_model import ChatMessageModel


class ChatService:
    """Manages chat history persistence."""

    @staticmethod
    def _get_collection():
        return Database.get_collection(ChatMessageModel.collection_name)

    @staticmethod
    def save_message(user_id, question, answer, sources=None, document_id=None):
        """Save a Q&A exchange to chat history."""
        col = ChatService._get_collection()
        doc = ChatMessageModel.create_schema(
            user_id=user_id,
            question=question,
            answer=answer,
            sources=sources or [],
            document_id=document_id,
        )
        result = col.insert_one(doc)
        return str(result.inserted_id)

    @staticmethod
    def get_history(user_id, document_id=None, limit=20):
        """Get recent chat messages for a user, newest first."""
        col = ChatService._get_collection()
        query = {'user_id': user_id}
        if document_id:
            query['document_id'] = document_id

        messages = col.find(query).sort('created_at', -1).limit(limit)
        result = []
        for m in messages:
            result.append({
                'id':          str(m['_id']),
                'question':    m['question'],
                'answer':      m['answer'],
                'sources':     m.get('sources', []),
                'document_id': m.get('document_id'),
                'created_at':  m['created_at'].isoformat(),
            })
        # Return in chronological order (oldest first) for display
        return list(reversed(result))

    @staticmethod
    def clear_history(user_id, document_id=None):
        """Delete chat history. Returns count of deleted messages."""
        col = ChatService._get_collection()
        query = {'user_id': user_id}
        if document_id:
            query['document_id'] = document_id
        result = col.delete_many(query)
        return result.deleted_count
