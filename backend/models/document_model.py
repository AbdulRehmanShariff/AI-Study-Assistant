from datetime import datetime, timezone


class DocumentModel:
    """Document metadata schema for MongoDB."""
    collection_name = 'documents'

    @staticmethod
    def create_schema(user_id, original_name, file_path, file_type, file_size):
        """Create a new document metadata document.

        Args:
            user_id:       Owner's user ID string.
            original_name: Original filename from upload (e.g. 'lecture.pdf').
            file_path:     Path on disk where the file is saved.
            file_type:     'pdf' or 'txt'.
            file_size:     Size in bytes.
        """
        return {
            'user_id': user_id,
            'original_name': original_name,
            'file_path': file_path,
            'file_type': file_type,
            'file_size': file_size,
            'page_count': 0,
            'word_count': 0,
            'chunk_count': 0,
            'status': 'uploaded',          # uploaded | processing | ready | error
            'processing_error': None,
            'vector_store_path': None,
            'summary': {},                 # e.g., {'concise': '...', 'detailed': '...'}
            'uploaded_at': datetime.now(timezone.utc),
            'processed_at': None,
        }
