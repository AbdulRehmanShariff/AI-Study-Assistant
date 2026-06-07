import sys
import time
import numpy as np

sys.path.insert(0, '.')

print('=' * 60)
print('FAISS VECTOR STORE TESTS')
print('=' * 60)

# ---------------------------------------------------------------
# Test 1: FAISS unit test (no DB required)
# ---------------------------------------------------------------
print('\n[1] FAISS index build + search (unit test)...')
from utils.vector_store import FAISSVectorStore
from utils.embedder import Embedder

# Embed 6 sample texts
texts = [
    'Neural networks learn from training data using backpropagation',
    'Convolutional networks are used for image recognition tasks',
    'Transformers use self-attention to process sequential data',
    'Python is a popular programming language for data science',
    'BERT and GPT are large language models based on transformers',
    'Gradient descent optimizes neural network weights over epochs',
]
print('    Embedding 6 texts...')
embeddings = Embedder.embed_batch(texts)
metadata = [{'chunk_id': f'c{i}', 'document_id': 'doc1', 'chunk_index': i, 'text': t}
            for i, t in enumerate(texts)]

store = FAISSVectorStore('test_user_faiss')
store.build_from_embeddings(embeddings, metadata)
print(f'    Index built: {store.get_count()} vectors')

# Search for transformer-related content
query = 'How do transformer models work?'
q_emb = Embedder.embed_text(query)
results = store.search(q_emb, top_k=3)

print(f'\n    Query: "{query}"')
print(f'    Top {len(results)} results:')
for i, r in enumerate(results):
    print(f'      {i+1}. [{r["score"]:.4f}] {r["text"][:70]}...')

# Verify relevant results come first
top_result_text = results[0]['text'].lower()
relevant = 'transformer' in top_result_text or 'attention' in top_result_text or 'bert' in top_result_text
print(f'\n    Top result relevant: {relevant}')
print(f'    Top score: {results[0]["score"]:.4f}')

# ---------------------------------------------------------------
# Test 2: Save and reload index
# ---------------------------------------------------------------
print('\n[2] Save and reload index from disk...')
store.save()
print(f'    Saved to: {store.index_path}')

store2 = FAISSVectorStore('test_user_faiss')
loaded = store2.load()
print(f'    Loaded from disk: {loaded}')
print(f'    Vector count: {store2.get_count()}')

results2 = store2.search(q_emb, top_k=1)
same_result = results2[0]['chunk_id'] == results[0]['chunk_id']
print(f'    Same top result after reload: {same_result}')

# ---------------------------------------------------------------
# Test 3: Document filter search
# ---------------------------------------------------------------
print('\n[3] Search filtered by document...')
# Add second doc metadata
texts2 = ['Biology studies living organisms and their ecosystems',
          'Chemistry deals with atoms molecules and chemical reactions']
emb2 = Embedder.embed_batch(texts2)
meta2 = [{'chunk_id': f'd2c{i}', 'document_id': 'doc2', 'chunk_index': i, 'text': t}
         for i, t in enumerate(texts2)]
store2.add_embeddings(emb2, meta2)
store2.save()
print(f'    Total vectors: {store2.get_count()}')

bio_query = 'Tell me about biology and living organisms'
b_emb = Embedder.embed_text(bio_query)
doc2_results = store2.search_by_document(b_emb, 'doc2', top_k=2)
all_from_doc2 = all(r['document_id'] == 'doc2' for r in doc2_results)
print(f'    Doc filter results: {len(doc2_results)}')
print(f'    All from doc2: {all_from_doc2}')
if doc2_results:
    print(f'    Top result: {doc2_results[0]["text"][:60]}...')

# ---------------------------------------------------------------
# Test 4: Full pipeline via API (upload → search)
# ---------------------------------------------------------------
print('\n[4] Full API pipeline: upload -> auto-index -> search...')
import urllib.request, urllib.error, json

BASE = 'http://localhost:5000/api'

def post_json(path, data, token=None):
    body = json.dumps(data).encode()
    req = urllib.request.Request(f'{BASE}{path}', data=body,
        headers={'Content-Type': 'application/json'}, method='POST')
    if token: req.add_header('Authorization', f'Bearer {token}')
    try:
        r = urllib.request.urlopen(req, timeout=10)
        return json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read()), e.code

def post_multipart(path, filename, content, ctype, token=None):
    boundary = b'----B7291'
    body = (b'--' + boundary + b'\r\nContent-Disposition: form-data; name="file"; filename="'
            + filename.encode() + b'"\r\nContent-Type: ' + ctype.encode() + b'\r\n\r\n'
            + content + b'\r\n--' + boundary + b'--\r\n')
    req = urllib.request.Request(f'{BASE}{path}', data=body,
        headers={'Content-Type': f'multipart/form-data; boundary={boundary.decode()}'},
        method='POST')
    if token: req.add_header('Authorization', f'Bearer {token}')
    try:
        r = urllib.request.urlopen(req, timeout=10)
        return json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read()), e.code

try:
    login_data, _ = post_json('/auth/login', {'email': 'test@studyai.com', 'password': 'password123'})
    token = login_data.get('data', {}).get('token')
    print(f'    Login: {"OK" if token else "FAILED"}')

    if token:
        study_text = (
            'Chapter 1: Transformers and Self-Attention\n\n'
            'The transformer architecture introduced the self-attention mechanism. '
            'Self-attention allows the model to weigh the importance of different words when encoding a sequence. '
            'BERT uses bidirectional transformers for pre-training language models.\n\n'
            'Chapter 2: Recurrent Neural Networks\n\n'
            'RNNs process sequences step by step, maintaining a hidden state. '
            'LSTMs solve the vanishing gradient problem in vanilla RNNs. '
            'GRUs are a simplified version of LSTMs with fewer parameters.\n\n'
            'Chapter 3: Convolutional Neural Networks\n\n'
            'CNNs use filters to detect local patterns in images. '
            'Pooling layers reduce spatial dimensions while retaining features. '
            'ResNets introduced skip connections to train very deep networks.'
        ).encode('utf-8')

        data4, s4 = post_multipart('/documents/upload', 'dl_notes.txt', study_text, 'text/plain', token)
        doc4 = data4.get('data', {}).get('document', {})
        doc4_id = doc4.get('id')
        print(f'    Upload: {s4} | words={doc4.get("word_count", 0)}')

        # Wait for processing
        print('    Waiting 15s for processing...')
        time.sleep(15)

        # Now search via VectorStoreService directly
        from config.database import Database
        Database.connect()
        from services.vector_store_service import VectorStoreService

        user_id = doc4.get('id')  # We don't have user_id directly here
        # Get user_id from auth/me
        req = urllib.request.Request(f'{BASE}/auth/me')
        req.add_header('Authorization', f'Bearer {token}')
        me = json.loads(urllib.request.urlopen(req, timeout=5).read())
        actual_user_id = me.get('data', {}).get('user', {}).get('id')

        results4 = VectorStoreService.search(actual_user_id, 'How does self-attention work in transformers?', top_k=3)
        print(f'    Search results: {len(results4)}')
        if results4:
            print(f'    Top result [{results4[0]["score"]:.4f}]: {results4[0]["text"][:70]}...')
            api_search_ok = results4[0]['score'] > 0.4
        else:
            api_search_ok = False
        print(f'    Relevant result found: {api_search_ok}')
except Exception as e:
    print(f'    API test error: {e}')
    api_search_ok = False

# ---------------------------------------------------------------
# Summary
# ---------------------------------------------------------------
print('\n' + '=' * 60)
all_pass = relevant and loaded and same_result and all_from_doc2 and api_search_ok
print(f'ALL TESTS PASSED: {all_pass}')
print('=' * 60)
