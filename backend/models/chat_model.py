from datetime import datetime, timezone


class ChatMessageModel:
    """Chat message schema for MongoDB."""
    collection_name = 'chat_messages'

    @staticmethod
    def create_schema(user_id, question, answer, sources=None, document_id=None):
        return {
            'user_id':     user_id,
            'document_id': document_id,
            'question':    question,
            'answer':      answer,
            'sources':     sources or [],
            'created_at':  datetime.now(timezone.utc),
        }
