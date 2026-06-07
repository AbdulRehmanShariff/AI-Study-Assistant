import re
from config.settings import Config


class TextChunker:
    """Splits text into overlapping chunks for embedding.

    Strategy (priority order):
      1. Split at paragraph boundaries (double newline)
      2. Split at sentence boundaries (. ! ?)
      3. Split at word boundaries (space)
      4. Hard cut at chunk_size as last resort

    This ensures chunks are semantically meaningful rather than
    arbitrarily cut mid-sentence.
    """

    def __init__(self, chunk_size=None, chunk_overlap=None):
        self.chunk_size = chunk_size or Config.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or Config.CHUNK_OVERLAP

    def split(self, text):
        """Split text into overlapping chunks.

        Args:
            text: Cleaned text string.

        Returns:
            List of dicts, each with:
              - text       (str)   the chunk content
              - chunk_index (int)  0-based position
              - char_start (int)   start char offset in original text
              - char_end   (int)   end char offset in original text
              - word_count (int)   number of words in chunk
        """
        if not text or not text.strip():
            return []

        text = text.strip()
        chunks = []
        start = 0
        chunk_index = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))

            # If we're not at the end, find a good split boundary
            if end < len(text):
                end = self._find_split_boundary(text, start, end)

            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append({
                    'text': chunk_text,
                    'chunk_index': chunk_index,
                    'char_start': start,
                    'char_end': end,
                    'word_count': len(chunk_text.split()),
                })
                chunk_index += 1

            # Move forward by (chunk_size - overlap) to create overlap
            next_start = start + self.chunk_size - self.chunk_overlap

            # Safety: always advance at least 1 char to avoid infinite loop
            if next_start <= start:
                next_start = start + 1

            start = next_start

        return chunks

    def _find_split_boundary(self, text, start, end):
        """Find the best split point near `end` within the chunk.

        Looks backwards from `end` to find:
        1. A paragraph break (\n\n)
        2. A sentence boundary (. ! ?)
        3. A word boundary (space)

        Falls back to hard cut at `end` if none found within
        the overlap window.
        """
        search_start = max(start, end - self.chunk_overlap)
        window = text[search_start:end]

        # 1. Paragraph break
        idx = window.rfind('\n\n')
        if idx != -1:
            return search_start + idx + 2

        # 2. Sentence boundary (. or ! or ? followed by space/newline)
        sentence_end = max(
            window.rfind('. '),
            window.rfind('! '),
            window.rfind('? '),
            window.rfind('.\n'),
            window.rfind('!\n'),
            window.rfind('?\n'),
        )
        if sentence_end != -1:
            return search_start + sentence_end + 2

        # 3. Word boundary (space or newline)
        word_end = max(window.rfind(' '), window.rfind('\n'))
        if word_end != -1:
            return search_start + word_end + 1

        # 4. Hard cut
        return end

    def split_with_metadata(self, text, document_id, user_id):
        """Split text and add document/user context to each chunk.

        Args:
            text:        Cleaned text string.
            document_id: String ID of the parent document.
            user_id:     String ID of the owner.

        Returns:
            List of chunk dicts ready to insert into MongoDB.
        """
        raw_chunks = self.split(text)
        enriched = []
        for chunk in raw_chunks:
            enriched.append({
                **chunk,
                'document_id': document_id,
                'user_id': user_id,
                'embedding': None,   # filled in Phase 8
            })
        return enriched
