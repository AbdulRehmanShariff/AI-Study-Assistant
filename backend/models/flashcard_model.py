from datetime import datetime, timezone


class FlashcardModel:
    """Flashcard set schema for MongoDB."""
    collection_name = 'flashcards'

    @staticmethod
    def create_schema(user_id, document_id, title, cards):
        return {
            'user_id': user_id,
            'document_id': document_id,
            'title': title,
            'cards': cards,  # [{question, answer}]
            'created_at': datetime.now(timezone.utc),
        }
