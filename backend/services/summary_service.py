import os
from bson import ObjectId
from config.database import Database
from models.document_model import DocumentModel
from utils.llm import GeminiLLM

class SummaryService:
    """Generates and caches AI summaries of uploaded documents."""

    # Summary style prompts
    STYLES = {
        'concise': (
            "Provide a concise, bulleted summary of the following text. "
            "Focus only on the most critical high-level points. "
            "Format with a brief introductory sentence, followed by 3-5 bullet points."
        ),
        'detailed': (
            "Provide a highly comprehensive, extensively detailed, and in-depth overview of the following text. "
            "Do not leave out any important information. Break the summary into logical sections using markdown headers (e.g., ### Key Concepts, ### In-Depth Details, ### Examples). "
            "Include all critical definitions, thorough explanations, nuanced points, and detailed conclusions drawn."
        ),
        'actionable': (
            "Summarize the following text by extracting actionable takeaways or practical steps. "
            "Format as a numbered list of actions or applications. "
            "Include a brief explanation of *why* each action matters based on the text."
        )
    }

    @staticmethod
    def _get_collection():
        return Database.get_collection(DocumentModel.collection_name)

    @staticmethod
    def generate_summary(user_id, document_id, style='concise'):
        """Generate a summary for a document or return a cached one.

        Args:
            user_id:     String user ID.
            document_id: String document ID.
            style:       'concise', 'detailed', or 'actionable'.

        Returns:
            String containing the generated markdown summary.
        Raises:
            ValueError: if document not found, invalid style, or missing text.
        """
        if style not in SummaryService.STYLES:
            raise ValueError(f"Invalid summary style. Must be one of: {list(SummaryService.STYLES.keys())}")

        col = SummaryService._get_collection()
        try:
            doc = col.find_one({'_id': ObjectId(document_id), 'user_id': user_id})
        except Exception:
            raise ValueError('Invalid document ID')

        if not doc:
            raise ValueError('Document not found')

        summary_cache = doc.get('summary', {})

        # Read the full extracted text from disk
        text_path = doc.get('text_path')
        if not text_path or not os.path.exists(text_path):
            raise ValueError('Document text not found or has not been extracted yet.')

        with open(text_path, 'r', encoding='utf-8') as f:
            full_text = f.read()

        if not full_text.strip():
            raise ValueError('Extracted text is empty.')
            
        # Prevent payload/token limit errors for massive files
        full_text = full_text[:1500000]

        # Call Gemini (with a 1M token context window, this can handle full books)
        system_instruction = "You are an expert academic summarizer."
        prompt = f"{SummaryService.STYLES[style]}\n\n---\nDOCUMENT TEXT:\n{full_text}"

        try:
            generated_summary = GeminiLLM.generate(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=0.4
            )
        except Exception as e:
            raise RuntimeError(f"Failed to generate summary: {e}")

        # Cache the result in MongoDB
        summary_cache[style] = generated_summary
        col.update_one(
            {'_id': ObjectId(document_id)},
            {'$set': {'summary': summary_cache}}
        )

        return generated_summary
