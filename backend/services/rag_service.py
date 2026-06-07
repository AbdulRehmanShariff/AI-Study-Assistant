from config.settings import Config
from utils.embedder import Embedder
from utils.llm import GeminiLLM
from services.vector_store_service import VectorStoreService


# RAG system prompt
SYSTEM_PROMPT = """You are an expert AI Study Assistant helping students deeply understand their study materials.

Your role:
- Answer questions based ONLY on the provided study material context.
- Be highly comprehensive and provide incredibly detailed, in-depth explanations. Do not give short summaries.
- Break down complex topics into easy-to-understand concepts.
- Extract and present as much relevant information from the context as possible, writing an extensive response similar to a detailed textbook chapter.
- Use bullet points, bold text, and formatting to structure your long answers.
- If the context doesn't contain enough information, say: "The provided materials don't cover this topic in detail."

Do NOT make up information not found in the context. Ensure your final output is long and informative."""


class RAGService:
    """Retrieval-Augmented Generation pipeline.

    Steps:
      1. Embed the user's question
      2. Retrieve top-K relevant chunks from FAISS
      3. Build a context-rich prompt
      4. Generate an answer via Gemini
      5. Return the answer with source metadata
    """

    @staticmethod
    def answer(user_id, question, document_id=None, top_k=None):
        """Answer a question using RAG.

        Args:
            user_id:     String user ID (for FAISS index lookup).
            question:    The user's question string.
            document_id: Optional — restrict search to one document.
            top_k:       Number of chunks to retrieve (default from config).

        Returns:
            dict with:
              answer   (str)  — Gemini's response
              sources  (list) — list of {chunk_id, document_id, text, score}
              question (str)  — echoed back
        Raises:
            ValueError: if question is empty or LLM not configured.
        """
        if not question or not question.strip():
            raise ValueError('Question cannot be empty')

        if not GeminiLLM.is_configured():
            raise ValueError(
                'Gemini API key not configured. '
                'Please add GEMINI_API_KEY to your backend/.env file.'
            )

        top_k = top_k or Config.TOP_K_RESULTS

        # Step 1 & 2: Embed question + retrieve chunks
        results = VectorStoreService.search(
            user_id=user_id,
            query_text=question,
            top_k=top_k,
            document_id=document_id,
        )

        if not results:
            return {
                'answer': (
                    "I couldn't find relevant information in your uploaded documents. "
                    "Please make sure you have uploaded study materials and they have been processed."
                ),
                'sources': [],
                'question': question,
            }

        # Step 3: Build context-rich prompt
        context = RAGService._build_context(results)
        prompt  = RAGService._build_prompt(question, context)

        # Step 4: Generate answer
        answer = GeminiLLM.generate(
            prompt=prompt,
            system_instruction=SYSTEM_PROMPT,
            temperature=0.3,
            max_tokens=4096,
        )

        # Step 5: Return with sources
        sources = [{
            'chunk_id':    r.get('chunk_id'),
            'document_id': r.get('document_id'),
            'text':        r.get('text', '')[:300],  # truncated preview
            'score':       round(r.get('score', 0), 4),
        } for r in results]

        return {
            'answer':   answer,
            'sources':  sources,
            'question': question,
        }

    @staticmethod
    def _build_context(results):
        """Format retrieved chunks into a numbered context block."""
        parts = []
        for i, r in enumerate(results, 1):
            parts.append(
                f'[Source {i}] (relevance: {r["score"]:.2f})\n{r["text"]}'
            )
        return '\n\n---\n\n'.join(parts)

    @staticmethod
    def _build_prompt(question, context):
        """Build the final prompt for Gemini."""
        return f"""Here is relevant content from the student's study materials:

{context}

---

Based on the above study material, please comprehensively answer this question in great detail:

{question}"""

    @staticmethod
    def check_llm_status():
        """Return status of the LLM configuration."""
        return {
            'configured': GeminiLLM.is_configured(),
            'model': GeminiLLM.MODEL,
        }
