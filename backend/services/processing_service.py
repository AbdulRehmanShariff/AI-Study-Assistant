import os
from datetime import datetime, timezone
from bson import ObjectId

from config.database import Database
from models.chunk_model import ChunkModel
from models.document_model import DocumentModel
from utils.chunker import TextChunker
from utils.embedder import Embedder


class ProcessingService:
    """Orchestrates the full document processing pipeline.

    Phase 7: Text chunking and chunk storage.
    Phase 8: Embedding generation (sentence-transformers).
    Phase 9: FAISS vector store indexing.
    """

    @staticmethod
    def _get_doc_collection():
        return Database.get_collection(DocumentModel.collection_name)

    @staticmethod
    def _get_chunk_collection():
        return Database.get_collection(ChunkModel.collection_name)

    @staticmethod
    def process_document(document_id, user_id):
        """Run the full processing pipeline for a document.

        Steps:
          1. Mark document as 'processing'
          2. Read extracted text from disk
          3. Split into chunks
          4. Generate embeddings for all chunks (batch)
          5. Store chunks + embeddings in MongoDB
          6. Build/update FAISS vector index for the user
          7. Mark document as 'ready' with chunk_count

        Args:
            document_id: String document ID.
            user_id:     String user ID (for ownership verification).

        Returns:
            dict with chunk_count and status.
        Raises:
            ValueError: if document not found or text file missing.
            Exception:  on any processing failure (status set to 'error').
        """
        doc_col = ProcessingService._get_doc_collection()
        chunk_col = ProcessingService._get_chunk_collection()

        # Fetch document
        try:
            doc = doc_col.find_one({
                '_id': ObjectId(document_id),
                'user_id': user_id
            })
        except Exception:
            raise ValueError('Invalid document ID')

        if not doc:
            raise ValueError('Document not found')

        # Mark as processing
        doc_col.update_one(
            {'_id': ObjectId(document_id)},
            {'$set': {'status': 'processing'}}
        )

        try:
            # 1. Read original file
            file_path = doc.get('file_path')
            if not file_path or not os.path.exists(file_path):
                raise ValueError('Original file missing or not saved')
                
            with open(file_path, 'rb') as f:
                file_bytes = f.read()
                
            ext = doc.get('file_type', 'unknown')
            
            # 2. Extract Text
            print(f'[INFO] Extracting text for {document_id}...')
            from utils.pdf_extractor import PDFExtractor
            from utils.text_cleaner import TextCleaner
            
            if ext == 'pdf':
                extracted = PDFExtractor.extract_from_bytes(file_bytes)
                page_count = extracted['page_count']
                word_count = extracted['word_count']
            else:
                extracted = TextCleaner.clean_txt_file(file_bytes)
                page_count = 0
                word_count = extracted['word_count']
                
            text = extracted['text']
            
            if not text.strip():
                raise ValueError('Document text is empty — nothing to process')

            # 3. Save extracted text
            text_path = doc.get('text_path') or (file_path + '.txt')
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(text)

            # Update document metadata
            doc_col.update_one(
                {'_id': ObjectId(document_id)},
                {'$set': {
                    'page_count': page_count,
                    'word_count': word_count,
                    'text_path': text_path
                }}
            )

            # Delete any existing chunks for this document (re-processing)
            chunk_col.delete_many({'document_id': document_id})

            # Chunk the text
            chunker = TextChunker()
            raw_chunks = chunker.split_with_metadata(text, document_id, user_id)

            if not raw_chunks:
                raise ValueError('No chunks produced — document may be too short')

            # Generate embeddings for all chunks in one batch
            print(f'[INFO] Embedding {len(raw_chunks)} chunks...')
            texts = [c['text'] for c in raw_chunks]
            embeddings = Embedder.embed_batch(texts, batch_size=32)

            # Build MongoDB documents for each chunk (with embeddings)
            chunk_docs = []
            for i, c in enumerate(raw_chunks):
                doc_schema = ChunkModel.create_schema(
                    document_id=c['document_id'],
                    user_id=c['user_id'],
                    chunk_index=c['chunk_index'],
                    text=c['text'],
                    char_start=c['char_start'],
                    char_end=c['char_end'],
                    word_count=c['word_count'],
                )
                # Store embedding as a list (MongoDB-compatible)
                doc_schema['embedding'] = Embedder.embedding_to_list(embeddings[i])
                chunk_docs.append(doc_schema)

            # Bulk insert chunks with embeddings
            chunk_col.insert_many(chunk_docs)
            chunk_count = len(chunk_docs)

            # Build / update FAISS index for this user
            print(f'[INFO] Building FAISS index for user {user_id[:8]}...')
            try:
                from services.vector_store_service import VectorStoreService
                VectorStoreService.build_index_for_user(user_id)
            except Exception as faiss_err:
                # Non-fatal: index can be rebuilt on demand during search
                print(f'[WARNING] FAISS index build failed: {faiss_err}')

            # Mark document as ready
            doc_col.update_one(
                {'_id': ObjectId(document_id)},
                {'$set': {
                    'status': 'ready',
                    'chunk_count': chunk_count,
                    'processed_at': datetime.now(timezone.utc),
                    'processing_error': None,
                }}
            )

            return {
                'document_id': document_id,
                'chunk_count': chunk_count,
                'status': 'ready',
            }

        except Exception as e:
            # Mark document as error
            doc_col.update_one(
                {'_id': ObjectId(document_id)},
                {'$set': {
                    'status': 'error',
                    'processing_error': str(e),
                }}
            )
            raise

    @staticmethod
    def get_chunks(document_id, user_id):
        """Retrieve all chunks for a document, ordered by index.

        Args:
            document_id: String document ID.
            user_id:     String user ID.

        Returns:
            List of chunk dicts (without embedding arrays).
        """
        chunk_col = ProcessingService._get_chunk_collection()
        chunks = chunk_col.find(
            {'document_id': document_id, 'user_id': user_id},
            {'embedding': 0}  # Exclude large embedding arrays from listing
        ).sort('chunk_index', 1)

        return [{
            'id': str(c['_id']),
            'chunk_index': c['chunk_index'],
            'text': c['text'],
            'char_start': c['char_start'],
            'char_end': c['char_end'],
            'word_count': c['word_count'],
        } for c in chunks]

    @staticmethod
    def delete_chunks(document_id):
        """Delete all chunks for a document.

        Called when a document is deleted.
        """
        chunk_col = ProcessingService._get_chunk_collection()
        result = chunk_col.delete_many({'document_id': document_id})
        return result.deleted_count

    @staticmethod
    def ensure_chunk_indexes():
        """Create MongoDB indexes for the chunks collection."""
        db = Database.get_db()
        if db is None:
            return
        db.chunks.create_index('document_id')
        db.chunks.create_index([('document_id', 1), ('chunk_index', 1)])
        db.chunks.create_index('user_id')
