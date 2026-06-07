import numpy as np
from config.database import Database
from utils.vector_store import FAISSVectorStore
from utils.embedder import Embedder


class VectorStoreService:
    """Manages per-user FAISS indexes.

    Responsibilities:
    - Build/rebuild the FAISS index for a user from their MongoDB chunks
    - Search across all of a user's documents
    - Search within a specific document
    - Rebuild index when documents are deleted
    """

    # In-memory cache: user_id → FAISSVectorStore
    _store_cache = {}

    @staticmethod
    def _get_store(user_id, load_from_disk=True):
        """Get or create a FAISSVectorStore for a user."""
        if user_id not in VectorStoreService._store_cache:
            store = FAISSVectorStore(user_id)
            if load_from_disk:
                store.load()
            VectorStoreService._store_cache[user_id] = store
        return VectorStoreService._store_cache[user_id]

    @staticmethod
    def build_index_for_user(user_id):
        """Build a fresh FAISS index from all embedded chunks in MongoDB.

        Called after a new document is processed (chunked + embedded).

        Args:
            user_id: String user ID.

        Returns:
            dict with vector_count.
        """
        db = Database.get_db()
        if db is None:
            raise RuntimeError('Database not connected')

        # Fetch all embedded chunks for this user
        chunks = list(db.chunks.find(
            {'user_id': user_id, 'embedding': {'$ne': None}},
            {'_id': 1, 'document_id': 1, 'chunk_index': 1, 'text': 1, 'embedding': 1}
        ))

        if not chunks:
            return {'vector_count': 0}

        # Build embeddings matrix and metadata list
        embeddings = []
        metadata   = []
        for chunk in chunks:
            emb = chunk.get('embedding')
            if emb is None:
                continue
            embeddings.append(np.array(emb, dtype=np.float32))
            metadata.append({
                'chunk_id':    str(chunk['_id']),
                'document_id': chunk['document_id'],
                'chunk_index': chunk['chunk_index'],
                'text':        chunk['text'],
            })

        embeddings_matrix = np.stack(embeddings)

        # Build and save the index
        store = FAISSVectorStore(user_id)
        store.build_from_embeddings(embeddings_matrix, metadata)
        store.save()

        # Update in-memory cache
        VectorStoreService._store_cache[user_id] = store

        print(f'[OK] FAISS index built for user {user_id[:8]}: {len(embeddings)} vectors')
        return {'vector_count': len(embeddings)}

    @staticmethod
    def search(user_id, query_text, top_k=5, document_id=None):
        """Semantic search across a user's documents.

        Args:
            user_id:     String user ID.
            query_text:  Natural language query string.
            top_k:       Number of results.
            document_id: If provided, restrict search to this document.

        Returns:
            List of result dicts: {chunk_id, document_id, text,
                                   chunk_index, score}
        """
        if not query_text or not query_text.strip():
            return []

        # Embed the query
        query_embedding = Embedder.embed_text(query_text)

        # Get user's store (load from disk if needed)
        store = VectorStoreService._get_store(user_id, load_from_disk=True)

        if store.get_count() == 0:
            # Try rebuilding from DB
            VectorStoreService.build_index_for_user(user_id)
            store = VectorStoreService._get_store(user_id, load_from_disk=False)
            if store.get_count() == 0:
                return []

        if document_id:
            return store.search_by_document(query_embedding, document_id, top_k=top_k)
        else:
            return store.search(query_embedding, top_k=top_k, min_score=0.0)

    @staticmethod
    def rebuild_after_delete(user_id):
        """Rebuild the FAISS index after a document has been deleted.

        Removes the cached store and rebuilds from remaining DB chunks.
        """
        # Evict from cache so it's rebuilt fresh
        VectorStoreService._store_cache.pop(user_id, None)

        # Delete old index files
        store = FAISSVectorStore(user_id)
        store.delete_files()

        # Rebuild from remaining chunks
        return VectorStoreService.build_index_for_user(user_id)

    @staticmethod
    def get_index_stats(user_id):
        """Return stats about the user's FAISS index."""
        store = VectorStoreService._get_store(user_id, load_from_disk=True)
        return {
            'vector_count': store.get_count(),
            'index_exists':  store.exists(),
        }
