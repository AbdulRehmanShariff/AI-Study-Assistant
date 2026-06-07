from datetime import datetime, timezone


class QuizResultModel:
    """Quiz result schema for MongoDB."""
    collection_name = 'quiz_results'

    @staticmethod
    def create_schema(user_id, quiz_id, score, total, percentage, answers):
        return {
            'user_id': user_id,
            'quiz_id': quiz_id,
            'score': score,
            'total': total,
            'percentage': percentage,
            'answers': answers,  # [{question_index, user_answer, is_correct}]
            'completed_at': datetime.now(timezone.utc),
        }
