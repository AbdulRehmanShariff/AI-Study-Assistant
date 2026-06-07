import os
import json
from bson import ObjectId
from config.database import Database
from models.document_model import DocumentModel
from models.quiz_model import QuizModel
from utils.llm import GeminiLLM

class QuizService:
    """Generates AI multiple-choice quizzes from documents."""

    @staticmethod
    def _get_doc_collection():
        return Database.get_collection(DocumentModel.collection_name)

    @staticmethod
    def _get_quiz_collection():
        return Database.get_collection(QuizModel.collection_name)

    @staticmethod
    def generate_quiz(user_id, document_id, count=5):
        """Generate a new multiple-choice quiz for a document.

        Args:
            user_id: String user ID.
            document_id: String document ID.
            count: Number of questions to generate.

        Returns:
            The generated quiz dict.
        """
        # 1. Fetch document
        col = QuizService._get_doc_collection()
        try:
            doc = col.find_one({'_id': ObjectId(document_id), 'user_id': user_id})
        except Exception:
            raise ValueError('Invalid document ID')

        if not doc:
            raise ValueError('Document not found')

        # 2. Check if a quiz already exists
        quiz_col = QuizService._get_quiz_collection()
        existing = quiz_col.find_one({'document_id': document_id, 'user_id': user_id})
        if existing:
            existing['_id'] = str(existing['_id'])
            return existing

        # 3. Read document text
        text_path = doc.get('text_path')
        if not text_path or not os.path.exists(text_path):
            raise ValueError('Document text not found or has not been extracted yet.')

        with open(text_path, 'r', encoding='utf-8') as f:
            full_text = f.read()

        if not full_text.strip():
            raise ValueError('Extracted text is empty.')
            
        # Prevent payload/token limit errors for massive files
        full_text = full_text[:1500000]

        # 4. Prompt Gemini to generate JSON quiz
        system_instruction = "You are an expert educator who designs challenging multiple-choice questions to test deep comprehension. Your explanations should be highly detailed."
        prompt = (
            f"Based on the following document text, generate exactly {count} multiple-choice questions.\n"
            f"Focus on the most important concepts and ensure distractors (incorrect options) are plausible.\n"
            f"Return ONLY a valid JSON array where each object has:\n"
            f"  - 'question': The question string\n"
            f"  - 'options': An array of exactly 4 string options\n"
            f"  - 'correct_index': An integer (0 to 3) representing the index of the correct option\n"
            f"  - 'explanation': A highly detailed, in-depth string explaining why the correct answer is right and why the distractors are wrong.\n"
            f"CRITICAL: You MUST randomize the 'correct_index' across the questions so it is equally likely to be 0, 1, 2, or 3. Do NOT make it the same for every question.\n"
            f"Do not include markdown code block formatting (like ```json), just the raw JSON array.\n\n"
            f"---\nDOCUMENT TEXT:\n{full_text}"
        )

        try:
            result_text = GeminiLLM.generate(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=0.4
            )
            # Clean up potential markdown formatting from Gemini
            cleaned_text = result_text.strip()
            if cleaned_text.startswith('```json'):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.startswith('```'):
                cleaned_text = cleaned_text[3:]
            if cleaned_text.endswith('```'):
                cleaned_text = cleaned_text[:-3]
            
            questions = json.loads(cleaned_text.strip())
            
            if not isinstance(questions, list):
                raise ValueError("LLM did not return a JSON array")
        except Exception as e:
            raise RuntimeError(f"Failed to generate quiz: {e}\nResponse was: {result_text}")

        # 5. Save to MongoDB
        title = doc.get('original_name', 'Document') + ' Quiz'
        quiz_doc = QuizModel.create_schema(user_id, document_id, title, questions)
        res = quiz_col.insert_one(quiz_doc)
        quiz_doc['_id'] = str(res.inserted_id)

        return quiz_doc

    @staticmethod
    def get_quiz(user_id, document_id):
        """Get a quiz for a specific document."""
        quiz_col = QuizService._get_quiz_collection()
        quiz_doc = quiz_col.find_one({'document_id': document_id, 'user_id': user_id})
        if quiz_doc:
            quiz_doc['_id'] = str(quiz_doc['_id'])
        return quiz_doc
