import os
import numpy as np
from config.settings import Config


class Embedder:
    """Generates text embeddings using sentence-transformers.

    Uses a singleton pattern so the model is loaded only once
    per process — loading takes ~5s and uses ~90MB RAM.

    Model: all-MiniLM-L6-v2
    Output: 384-dimensional float32 vectors
    """

    _model = None
    _model_name = None

    @classmethod
    def get_model(cls):
        """Load and cache the embedding model (singleton)."""
        model_name = Config.EMBEDDING_MODEL
        if cls._model is None or cls._model_name != model_name:
            try:
                from sentence_transformers import SentenceTransformer
                print(f'[INFO] Loading embedding model: {model_name}')
                cls._model = SentenceTransformer(model_name)
                cls._model_name = model_name
                print(f'[OK] Embedding model loaded (dim={Config.EMBEDDING_DIMENSION})')
            except Exception as e:
                raise RuntimeError(f'Failed to load embedding model: {e}')
        return cls._model

    @classmethod
    def embed_text(cls, text):
        """Generate an embedding for a single text string.

        Args:
            text: String to embed.

        Returns:
            numpy float32 array of shape (384,)
        """
        model = cls.get_model()
        embedding = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
        return embedding.astype(np.float32)

    @classmethod
    def embed_batch(cls, texts, batch_size=32, show_progress=False):
        """Generate embeddings for a list of texts efficiently.

        Args:
            texts:         List of strings.
            batch_size:    Number of texts to encode at once (default 32).
            show_progress: Show tqdm progress bar (default False).

        Returns:
            numpy float32 array of shape (len(texts), 384)
        """
        if not texts:
            return np.array([], dtype=np.float32)

        model = cls.get_model()
        embeddings = model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=show_progress,
        )
        return embeddings.astype(np.float32)

    @classmethod
    def embedding_to_list(cls, embedding):
        """Convert numpy embedding to a Python list for MongoDB storage."""
        if embedding is None:
            return None
        if isinstance(embedding, np.ndarray):
            return embedding.tolist()
        return embedding

    @classmethod
    def list_to_embedding(cls, lst):
        """Convert a stored list back to a numpy array for FAISS."""
        if lst is None:
            return None
        return np.array(lst, dtype=np.float32)

    @classmethod
    def is_model_loaded(cls):
        """Check if the model is currently loaded."""
        return cls._model is not None
