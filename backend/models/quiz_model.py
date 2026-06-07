from datetime import datetime, timezone

class QuizModel:
    """Quiz schema for MongoDB."""
    collection_name = 'quizzes'

    @staticmethod
    def create_schema(user_id, document_id, title, questions):
        """Create a new quiz document.

        Args:
            user_id:     String user ID.
            document_id: String document ID the quiz belongs to.
            title:       Title of the quiz.
            questions:   List of dicts: 
                         [{'question': '...', 'options': ['A','B','C','D'], 'correct_index': 0, 'explanation': '...'}, ...]
        """
        return {
            'user_id': user_id,
            'document_id': document_id,
            'title': title,
            'questions': questions,
            'created_at': datetime.now(timezone.utc)
        }
