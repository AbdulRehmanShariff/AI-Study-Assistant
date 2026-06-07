import os
import uuid
import threading
from datetime import datetime, timezone
from bson import ObjectId

from config.settings import Config
from config.database import Database
from models.document_model import DocumentModel
from utils.pdf_extractor import PDFExtractor
from utils.text_cleaner import TextCleaner


# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'txt'}
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'text/plain',
    'application/octet-stream',  # Some browsers send this for .txt
}


class DocumentService:
    """Business logic for document management."""

    @staticmethod
    def _get_collection():
        return Database.get_collection(DocumentModel.collection_name)

    @staticmethod
    def _allowed_file(filename):
        """Check if file extension is allowed."""
        return (
            '.' in filename
            and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
        )

    @staticmethod
    def _serialize_document(doc):
        """Convert MongoDB doc to safe dict."""
        return {
            'id': str(doc['_id']),
            'original_name': doc.get('original_name', doc.get('file_name', '')),
            'file_type': doc.get('file_type', 'unknown'),
            'file_size': doc.get('file_size', 0),
            'page_count': doc.get('page_count', 0),
            'word_count': doc.get('word_count', 0),
            'chunk_count': doc.get('chunk_count', 0),
            'status': doc.get('status', 'uploaded'),
            'processing_error': doc.get('processing_error'),
            'uploaded_at': doc['uploaded_at'].isoformat(),
            'processed_at': (
                doc['processed_at'].isoformat()
                if doc.get('processed_at') else None
            ),
        }

    @staticmethod
    def upload(user_id, file_storage):
        """Handle a file upload from Flask's request.files.

        Args:
            user_id:      Authenticated user's ID.
            file_storage: Werkzeug FileStorage object.

        Returns:
            Serialized document dict.
        Raises:
            ValueError: on invalid file type, size, or extraction failure.
        """
        if not file_storage or not file_storage.filename:
            raise ValueError('No file provided')

        filename = file_storage.filename
        if not DocumentService._allowed_file(filename):
            raise ValueError(
                f'File type not allowed. Only PDF and TXT files are accepted.'
            )

        # Read file bytes
        file_bytes = file_storage.read()
        file_size = len(file_bytes)

        if file_size == 0:
            raise ValueError('Uploaded file is empty')

        max_bytes = Config.MAX_FILE_SIZE_MB * 1024 * 1024
        if file_size > max_bytes:
            raise ValueError(
                f'File too large. Maximum size is {Config.MAX_FILE_SIZE_MB}MB'
            )

        # Determine file type
        ext = filename.rsplit('.', 1)[1].lower()

        # Save file to disk with unique name to avoid collisions
        safe_name = f"{uuid.uuid4().hex}_{filename}"
        upload_dir = os.path.join(os.getcwd(), Config.UPLOAD_FOLDER, user_id)
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, safe_name)

        with open(file_path, 'wb') as f:
            f.write(file_bytes)

        # Save metadata to MongoDB
        col = DocumentService._get_collection()
        doc = DocumentModel.create_schema(
            user_id=user_id,
            original_name=filename,
            file_path=file_path,
            file_type=ext,
            file_size=file_size,
        )
        doc['page_count'] = 0
        doc['word_count'] = 0
        doc['text_path'] = file_path + '.txt'
        doc['status'] = 'uploaded'

        result = col.insert_one(doc)
        doc['_id'] = result.inserted_id
        document_id = str(result.inserted_id)

        # Trigger chunking in a background thread so upload returns fast
        DocumentService._trigger_processing(document_id, user_id)

        return DocumentService._serialize_document(doc)

    @staticmethod
    def _trigger_processing(document_id, user_id):
        """Start document processing in a background thread."""
        def run():
            try:
                from services.processing_service import ProcessingService
                ProcessingService.process_document(document_id, user_id)
                print(f'[OK] Processed document {document_id}')
            except Exception as e:
                print(f'[ERROR] Processing failed for {document_id}: {e}')

        thread = threading.Thread(target=run, daemon=True)
        thread.start()

    @staticmethod
    def list_documents(user_id):
        """List all documents for a user, newest first.

        Returns:
            List of serialized document dicts.
        """
        col = DocumentService._get_collection()
        docs = col.find({'user_id': user_id}).sort('uploaded_at', -1)
        return [DocumentService._serialize_document(d) for d in docs]

    @staticmethod
    def get_document(user_id, document_id):
        """Get a single document by ID.

        Returns:
            Serialized document dict.
        Raises:
            ValueError: if not found or not owned by user.
        """
        col = DocumentService._get_collection()
        try:
            doc = col.find_one({'_id': ObjectId(document_id), 'user_id': user_id})
        except Exception:
            raise ValueError('Invalid document ID')

        if not doc:
            raise ValueError('Document not found')

        return DocumentService._serialize_document(doc)

    @staticmethod
    def delete_document(user_id, document_id):
        """Delete a document and its files from disk.

        Raises:
            ValueError: if not found or not owned by user.
        """
        col = DocumentService._get_collection()
        try:
            doc = col.find_one({'_id': ObjectId(document_id), 'user_id': user_id})
        except Exception:
            raise ValueError('Invalid document ID')

        if not doc:
            raise ValueError('Document not found')

        # Delete files from disk
        for path_key in ['file_path', 'text_path', 'vector_store_path']:
            path = doc.get(path_key)
            if path and os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass  # Non-critical: file may already be deleted

        # Remove chunks from MongoDB
        try:
            from services.processing_service import ProcessingService
            ProcessingService.delete_chunks(document_id)
        except Exception:
            pass  # Non-critical

        # Remove document from DB
        col.delete_one({'_id': ObjectId(document_id)})

        # Rebuild FAISS index without the deleted document's chunks
        try:
            from services.vector_store_service import VectorStoreService
            VectorStoreService.rebuild_after_delete(user_id)
        except Exception:
            pass  # Non-critical — index rebuilt on next search

    @staticmethod
    def get_status(user_id, document_id):
        """Get the processing status of a document.

        Returns:
            dict with status, chunk_count, processing_error.
        """
        doc = DocumentService.get_document(user_id, document_id)
        return {
            'id': doc['id'],
            'status': doc['status'],
            'chunk_count': doc['chunk_count'],
            'processing_error': doc['processing_error'],
        }
