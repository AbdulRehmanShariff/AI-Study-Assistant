import sys
import numpy as np

print('=' * 55)
print('EMBEDDING TESTS')
print('=' * 55)

# Test 1: Model loads
print('\n[1] Loading embedding model...')
try:
    sys.path.insert(0, '.')
    from utils.embedder import Embedder
    model = Embedder.get_model()
    print(f'    Model loaded : OK')
    print(f'    Model type   : {type(model).__name__}')
except Exception as e:
    print(f'    FAILED: {e}')
    sys.exit(1)

# Test 2: Single embedding
print('\n[2] Single text embedding...')
text = 'Machine learning is a subset of artificial intelligence.'
emb = Embedder.embed_text(text)
print(f'    Shape    : {emb.shape}')
print(f'    Dtype    : {emb.dtype}')
print(f'    Dim = 384: {emb.shape[0] == 384}')
print(f'    Normalized: {abs(np.linalg.norm(emb) - 1.0) < 1e-5}')

# Test 3: Batch embedding
print('\n[3] Batch embedding (5 texts)...')
texts = [
    'Introduction to neural networks',
    'Supervised learning algorithms',
    'Gradient descent optimization',
    'Convolutional neural networks for images',
    'Natural language processing basics',
]
batch_embs = Embedder.embed_batch(texts)
print(f'    Shape         : {batch_embs.shape}')
print(f'    Expected shape: (5, 384)')
print(f'    Shape OK      : {batch_embs.shape == (5, 384)}')

# Test 4: Similarity check (similar texts should be close)
print('\n[4] Semantic similarity test...')
emb_a = Embedder.embed_text('The cat sat on the mat')
emb_b = Embedder.embed_text('A cat is sitting on a mat')
emb_c = Embedder.embed_text('Quantum physics equations')
sim_ab = float(np.dot(emb_a, emb_b))
sim_ac = float(np.dot(emb_a, emb_c))
print(f'    Similarity (similar texts): {sim_ab:.4f}')
print(f'    Similarity (unrelated):     {sim_ac:.4f}')
print(f'    Similar > Unrelated: {sim_ab > sim_ac}')

# Test 5: MongoDB serialization roundtrip
print('\n[5] MongoDB serialization (list <-> numpy)...')
original = Embedder.embed_text('Test serialization')
as_list  = Embedder.embedding_to_list(original)
restored = Embedder.list_to_embedding(as_list)
diff = np.max(np.abs(original - restored))
print(f'    Max diff after roundtrip: {diff:.2e}')
print(f'    Roundtrip OK: {diff < 1e-6}')

print('\n' + '=' * 55)
all_pass = (
    emb.shape[0] == 384
    and batch_embs.shape == (5, 384)
    and sim_ab > sim_ac
    and diff < 1e-6
)
print(f'ALL TESTS PASSED: {all_pass}')
print('=' * 55)
