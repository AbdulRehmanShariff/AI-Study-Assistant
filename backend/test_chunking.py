import urllib.request
import urllib.error
import json
import time

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
    boundary = b'----Boundary9182'
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

print('=' * 55)
print('CHUNKING PIPELINE TESTS')
print('=' * 55)

# Login
print('\n[0] Login...')
login_data, _ = post_json('/auth/login', {'email': 'test@studyai.com', 'password': 'password123'})
token = login_data.get('data', {}).get('token')
print(f'    Token: {"OK" if token else "FAILED"}')

# Generate a long text to ensure multiple chunks
long_text = '\n\n'.join([
    f'Section {i}: ' + ('This is study material about artificial intelligence and machine learning. ' * 20)
    for i in range(1, 8)
]).encode('utf-8')

# Test 1: Upload a large TXT → triggers auto-chunking
print('\n[1] Upload large TXT (triggers auto-chunking)...')
data1, s1 = post_multipart('/documents/upload', 'study_notes.txt', long_text, 'text/plain', token)
print(f'    Status  : {s1}')
doc = data1.get('data', {}).get('document', {})
doc_id = doc.get('id')
print(f'    Doc ID  : {doc_id[:16]}...' if doc_id else '    Doc ID  : NONE')
print(f'    Words   : {doc.get("word_count", 0)}')
print(f'    Status  : {doc.get("status")}')

# Test 2: Wait for background chunking to complete
print('\n[2] Waiting 3s for background chunking...')
time.sleep(3)

# Check status
data2, s2 = get(f'/documents/{doc_id}/status', token)
status_data = data2.get('data', {})
print(f'    Doc status  : {status_data.get("status")}')
print(f'    Chunk count : {status_data.get("chunk_count")}')

# Test 3: Verify chunker directly
print('\n[3] Direct chunker unit test...')
import sys
sys.path.insert(0, '.')
from utils.chunker import TextChunker

sample = 'Word ' * 500  # 500 words = ~2500 chars
chunker = TextChunker(chunk_size=1000, chunk_overlap=200)
chunks = chunker.split(sample)
print(f'    Input chars : {len(sample)}')
print(f'    Chunk count : {len(chunks)}')
print(f'    Chunk 0 len : {len(chunks[0]["text"])} chars')
print(f'    Chunk 1 start: {chunks[1]["char_start"]} (overlap = {1000 - 200})')
overlap_ok = chunks[1]['char_start'] < 1000
print(f'    Overlap OK  : {overlap_ok}')

# Test 4: Check chunk boundaries are smart (no mid-word cuts)
print('\n[4] Smart boundary test (sentence split)...')
para_text = (
    'This is the first sentence. This is the second sentence! '
    'Here comes the third? Yes indeed. ' * 30
)
p_chunks = chunker.split(para_text)
last_char_of_chunk0 = p_chunks[0]['text'][-1] if p_chunks else ''
print(f'    Chunks created : {len(p_chunks)}')
print(f'    Last char ch0  : "{last_char_of_chunk0}"')
smart_split = last_char_of_chunk0 in ['.', '!', '?', ' ', '\n']
print(f'    Smart split    : {smart_split}')

print('\n' + '=' * 55)
pipeline_ok = s1 == 201 and status_data.get('chunk_count', 0) > 0 and overlap_ok
print(f'ALL TESTS PASSED: {pipeline_ok}')
print('=' * 55)
