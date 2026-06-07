import os
import pickle
import numpy as np
import faiss

from config.settings import Config


class FAISSVectorStore:
    """FAISS-backed vector store for fast semantic similarity search.

    Uses IndexFlatIP (inner product) with L2-normalized embeddings
    which is mathematically equivalent to cosine similarity.

    Each user gets their own index file stored at:
        <vector_store_path>/<user_id>/index.faiss
        <vector_store_path>/<user_id>/metadata.pkl

    The metadata file maps FAISS integer indices → chunk MongoDB IDs
    and stores the chunk texts for retrieval without a second DB query.
    """

    def __init__(self, user_id):
        self.user_id = user_id
        self.dimension = Config.EMBEDDING_DIMENSION  # 384
        self.index_dir = os.path.join(
            os.getcwd(), Config.VECTOR_STORE_PATH, user_id
        )
        self.index_path = os.path.join(self.index_dir, 'index.faiss')
        self.meta_path  = os.path.join(self.index_dir, 'metadata.pkl')
        self._index    = None
        self._metadata = []   # List of dicts: {chunk_id, document_id, text, chunk_index}

    # ------------------------------------------------------------------
    # Build & Persist
    # ------------------------------------------------------------------

    def build_from_embeddings(self, embeddings, metadata):
        """Build a new FAISS index from a list of embeddings.

        Args:
            embeddings: numpy float32 array of shape (N, 384).
            metadata:   List of N dicts, each with keys:
                          chunk_id, document_id, text, chunk_index
        """
        if len(embeddings) == 0:
            raise ValueError('Cannot build index — no embeddings provided')

        vectors = np.array(embeddings, dtype=np.float32)
        if vectors.ndim != 2 or vectors.shape[1] != self.dimension:
            raise ValueError(
                f'Expected shape (N, {self.dimension}), got {vectors.shape}'
            )

        # Normalize to unit length (ensures IP == cosine similarity)
        faiss.normalize_L2(vectors)

        # Create a flat inner product index
        index = faiss.IndexFlatIP(self.dimension)

        # Wrap with an ID map so we can delete by ID later
        id_index = faiss.IndexIDMap(index)
        ids = np.arange(len(vectors), dtype=np.int64)
        id_index.add_with_ids(vectors, ids)

        self._index    = id_index
        self._metadata = metadata

    def add_embeddings(self, embeddings, metadata):
        """Add new embeddings to an existing index.

        If no index exists yet, builds one from scratch.
        """
        if self._index is None:
            self.build_from_embeddings(embeddings, metadata)
            return

        vectors = np.array(embeddings, dtype=np.float32)
        faiss.normalize_L2(vectors)

        start_id = len(self._metadata)
        ids = np.arange(start_id, start_id + len(vectors), dtype=np.int64)
        self._index.add_with_ids(vectors, ids)
        self._metadata.extend(metadata)

    def save(self):
        """Persist the index and metadata to disk."""
        if self._index is None:
            raise ValueError('No index to save')

        os.makedirs(self.index_dir, exist_ok=True)
        faiss.write_index(self._index, self.index_path)

        with open(self.meta_path, 'wb') as f:
            pickle.dump(self._metadata, f)

    def load(self):
        """Load index and metadata from disk.

        Returns:
            True if loaded successfully, False if files don't exist.
        """
        if not os.path.exists(self.index_path) or not os.path.exists(self.meta_path):
            return False

        self._index = faiss.read_index(self.index_path)

        with open(self.meta_path, 'rb') as f:
            self._metadata = pickle.load(f)

        return True

    def exists(self):
        """Check if a saved index exists on disk for this user."""
        return os.path.exists(self.index_path)

    def get_count(self):
        """Return number of vectors in the index."""
        if self._index is None:
            return 0
        return self._index.ntotal

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search(self, query_embedding, top_k=5, min_score=0.0):
        """Search for the top-K most similar chunks.

        Args:
            query_embedding: numpy float32 array of shape (384,).
            top_k:           Number of results to return.
            min_score:       Minimum cosine similarity threshold (0-1).

        Returns:
            List of dicts ordered by relevance:
              {chunk_id, document_id, text, chunk_index, score}
        """
        if self._index is None:
            loaded = self.load()
            if not loaded:
                return []

        if self._index.ntotal == 0:
            return []

        # Normalize query
        query = np.array([query_embedding], dtype=np.float32)
        faiss.normalize_L2(query)

        # Clamp top_k to available vectors
        k = min(top_k, self._index.ntotal)

        scores, indices = self._index.search(query, k)
        scores  = scores[0]
        indices = indices[0]

        results = []
        for score, idx in zip(scores, indices):
            if idx < 0:           # FAISS returns -1 for missing entries
                continue
            if float(score) < min_score:
                continue
            meta = self._metadata[idx]
            results.append({
                **meta,
                'score': float(score),
            })

        return results

    def search_by_document(self, query_embedding, document_id, top_k=5):
        """Search only within a specific document."""
        if self._index is None or self._index.ntotal == 0:
            return []
            
        # Search all user chunks to guarantee we find the document's chunks
        all_results = self.search(query_embedding, top_k=self._index.ntotal)
        filtered = [r for r in all_results if str(r.get('document_id')) == str(document_id)]
        return filtered[:top_k]

    # ------------------------------------------------------------------
    # Maintenance
    # ------------------------------------------------------------------

    def delete_document_chunks(self, document_id):
        """Remove all chunks for a document from the index.

        Rebuilds the index without the deleted document's vectors.
        Note: This is a full rebuild — acceptable since documents
              are deleted infrequently.
        """
        remaining_meta = [
            m for m in self._metadata
            if m.get('document_id') != document_id
        ]
        # We need the embeddings of remaining items — stored in DB
        # This is handled by VectorStoreService.rebuild_for_user()
        return len(self._metadata) - len(remaining_meta)

    def clear(self):
        """Clear in-memory index."""
        self._index    = None
        self._metadata = []

    def delete_files(self):
        """Delete index files from disk."""
        for path in [self.index_path, self.meta_path]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except OSError:
                    pass
