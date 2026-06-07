import os
import json
from bson import ObjectId
from config.database import Database
from models.document_model import DocumentModel
from models.flashcard_model import FlashcardModel
from utils.llm import GeminiLLM

class FlashcardService:
    """Generates AI flashcards from documents and manages decks."""

    @staticmethod
    def _get_doc_collection():
        return Database.get_collection(DocumentModel.collection_name)

    @staticmethod
    def _get_flashcard_collection():
        return Database.get_collection(FlashcardModel.collection_name)

    @staticmethod
    def generate_flashcards(user_id, document_id, count=10):
        """Generate a new set of flashcards for a document.

        Args:
            user_id: String user ID.
            document_id: String document ID.
            count: Number of flashcards to generate.

        Returns:
            The generated deck dict.
        """
        # 1. Fetch document
        col = FlashcardService._get_doc_collection()
        try:
            doc = col.find_one({'_id': ObjectId(document_id), 'user_id': user_id})
        except Exception:
            raise ValueError('Invalid document ID')

        if not doc:
            raise ValueError('Document not found')

        # 2. Check if a deck already exists
        fc_col = FlashcardService._get_flashcard_collection()
        existing = fc_col.find_one({'document_id': document_id, 'user_id': user_id})
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

        system_instruction = "You are an expert educator who creates highly detailed, in-depth flashcards."
        prompt = (
            f"Based on the following document text, generate exactly {count} highly informative flashcards.\n"
            f"Focus on the most important concepts, definitions, and facts. The 'answer' for each flashcard must be comprehensive, providing in-depth explanations and contextual details rather than just a few words.\n"
            f"Return ONLY a valid JSON array where each object has a 'question' and 'answer' string field. "
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
            
            cards = json.loads(cleaned_text.strip())
            
            if not isinstance(cards, list):
                raise ValueError("LLM did not return a JSON array")
        except Exception as e:
            raise RuntimeError(f"Failed to generate flashcards: {e}\nResponse was: {result_text}")

        # 5. Save to MongoDB
        title = doc.get('original_name', 'Document') + ' Flashcards'
        deck = FlashcardModel.create_schema(user_id, document_id, title, cards)
        res = fc_col.insert_one(deck)
        deck['_id'] = str(res.inserted_id)

        return deck

    @staticmethod
    def get_flashcards(user_id, document_id):
        """Get flashcards for a specific document."""
        fc_col = FlashcardService._get_flashcard_collection()
        deck = fc_col.find_one({'document_id': document_id, 'user_id': user_id})
        if deck:
            deck['_id'] = str(deck['_id'])
        return deck
