import urllib.request
import urllib.error
import json
import time
import sys

BASE = 'http://localhost:5000/api'

def post_json(path, data, token=None):
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        f'{BASE}{path}', data=body,
        headers={'Content-Type': 'application/json'}, method='POST'
    )
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    try:
        r = urllib.request.urlopen(req, timeout=10)
        return json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read()), e.code

def get(path, token=None):
    req = urllib.request.Request(f'{BASE}{path}')
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    try:
        r = urllib.request.urlopen(req, timeout=10)
        return json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read()), e.code

def post_multipart(path, filename, content, ctype, token=None):
    boundary = b'----Boundary1234'
    body = (
        b'--' + boundary + b'\r\n'
        b'Content-Disposition: form-data; name="file"; filename="' + filename.encode() + b'"\r\n'
        b'Content-Type: ' + ctype.encode() + b'\r\n\r\n'
        + content + b'\r\n'
        b'--' + boundary + b'--\r\n'
    )
    req = urllib.request.Request(
        f'{BASE}{path}', data=body,
        headers={'Content-Type': f'multipart/form-data; boundary={boundary.decode()}'},
        method='POST'
    )
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    try:
        r = urllib.request.urlopen(req, timeout=10)
        return json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read()), e.code

print('=' * 60)
print('END-TO-END PIPELINE TEST: Upload -> Chunk -> Embed')
print('=' * 60)

# Step 1: Login
print('\n[1] Login...')
login_data, _ = post_json('/auth/login', {'email': 'test@studyai.com', 'password': 'password123'})
token = login_data.get('data', {}).get('token')
print(f'    Token: {"OK" if token else "FAILED"}')
if not token:
    sys.exit(1)

# Step 2: Upload a study document
print('\n[2] Uploading study document...')
study_text = '\n\n'.join([
    'Chapter 1: Neural Networks\n\nNeural networks are computing systems inspired by biological neural networks. They consist of layers of interconnected nodes that process information.',
    'Chapter 2: Deep Learning\n\nDeep learning uses multiple layers of neural networks to learn hierarchical representations of data. It has revolutionized computer vision and NLP.',
    'Chapter 3: Transformers\n\nTransformers use self-attention mechanisms to process sequential data. Models like BERT and GPT are based on the transformer architecture.',
    'Chapter 4: Training Methods\n\nBackpropagation is used to train neural networks by computing gradients. Optimizers like Adam and SGD update model weights to minimize loss.',
    'Chapter 5: Applications\n\nDeep learning is applied in image recognition, speech synthesis, machine translation, and recommendation systems across many industries.',
] * 4).encode('utf-8')  # Repeat 4x to get more chunks

data2, s2 = post_multipart('/documents/upload', 'ai_study_guide.txt', study_text, 'text/plain', token)
doc = data2.get('data', {}).get('document', {})
doc_id = doc.get('id')
print(f'    Status  : {s2}')
print(f'    Words   : {doc.get("word_count", 0):,}')
print(f'    Doc ID  : {doc_id[:16] if doc_id else "NONE"}...')

# Step 3: Wait for background processing (chunking + embedding)
# First run: model needs to load (~20s) then embed
print('\n[3] Waiting for chunking + embedding (up to 35s)...')
for i in range(0, 36, 3):
    time.sleep(3)
    status_data, _ = get(f'/documents/{doc_id}/status', token)
    current_status = status_data.get('data', {}).get('status', '?')
    chunks = status_data.get('data', {}).get('chunk_count', 0)
    elapsed = (i + 1) * 3
    print(f'    t+{elapsed:02d}s: status={current_status}, chunks={chunks}')
    if current_status in ('ready', 'error'):
        break

# Step 4: Verify final status
print('\n[4] Final document status...')
final_data, _ = get(f'/documents/{doc_id}/status', token)
final = final_data.get('data', {})
print(f'    Status      : {final.get("status")}')
print(f'    Chunk count : {final.get("chunk_count")}')
print(f'    Error       : {final.get("processing_error")}')

# Step 5: Verify embeddings in MongoDB directly
print('\n[5] Verifying embeddings in MongoDB...')
sys.path.insert(0, '.')
from config.database import Database
from bson import ObjectId

db = Database.connect()
if db is not None:
    chunk = db.chunks.find_one({'document_id': doc_id})
    if chunk:
        emb = chunk.get('embedding')
        print(f'    Chunk found      : YES')
        print(f'    Has embedding    : {emb is not None}')
        print(f'    Embedding length : {len(emb) if emb else 0}')
        print(f'    Dim = 384        : {len(emb) == 384 if emb else False}')
        total_chunks = db.chunks.count_documents({'document_id': doc_id})
        embedded_chunks = db.chunks.count_documents({'document_id': doc_id, 'embedding': {'$ne': None}})
        print(f'    Total chunks     : {total_chunks}')
        print(f'    Embedded chunks  : {embedded_chunks}')
        print(f'    All embedded     : {total_chunks == embedded_chunks}')
    else:
        print('    No chunks found in DB!')

print('\n' + '=' * 60)
pipeline_ok = (
    s2 == 201
    and final.get('status') == 'ready'
    and final.get('chunk_count', 0) > 0
    and emb is not None
    and len(emb) == 384
    and total_chunks == embedded_chunks
)
print(f'FULL PIPELINE TEST PASSED: {pipeline_ok}')
print('=' * 60)
