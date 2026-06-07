from datetime import datetime, timezone


class ChunkModel:
    """Text chunk schema for MongoDB.

    Each chunk is a portion of a document's extracted text,
    ready to be embedded and stored in FAISS.
    """
    collection_name = 'chunks'

    @staticmethod
    def create_schema(document_id, user_id, chunk_index,
                      text, char_start, char_end, word_count):
        """Create a chunk document.

        Args:
            document_id: String ID of the parent document.
            user_id:     String ID of the owner.
            chunk_index: 0-based position within the document.
            text:        Chunk text content.
            char_start:  Start character offset in original text.
            char_end:    End character offset in original text.
            word_count:  Number of words in this chunk.
        """
        return {
            'document_id': document_id,
            'user_id': user_id,
            'chunk_index': chunk_index,
            'text': text,
            'char_start': char_start,
            'char_end': char_end,
            'word_count': word_count,
            'embedding': None,       # numpy array — filled in Phase 8
            'created_at': datetime.now(timezone.utc),
        }
