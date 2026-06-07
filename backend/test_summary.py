import urllib.request
import urllib.error
import json
import sys
import time

BASE = 'http://localhost:5000/api'

def post_json(path, data, token=None):
    body = json.dumps(data).encode()
    req = urllib.request.Request(f'{BASE}{path}', data=body,
        headers={'Content-Type': 'application/json'}, method='POST')
    if token: req.add_header('Authorization', f'Bearer {token}')
    try:
        r = urllib.request.urlopen(req, timeout=90)
        return json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read()), e.code

def get(path, token=None):
    req = urllib.request.Request(f'{BASE}{path}')
    if token: req.add_header('Authorization', f'Bearer {token}')
    try:
        r = urllib.request.urlopen(req, timeout=10)
        return json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read()), e.code

print('=' * 60)
print('SUMMARY GENERATION API TEST')
print('=' * 60)

# Login
print('\n[1] Login...')
login_data, _ = post_json('/auth/login', {'email': 'test@studyai.com', 'password': 'password123'})
token = login_data.get('data', {}).get('token')
print(f'    Token: {"OK" if token else "FAILED"}')
if not token: sys.exit(1)

# Get documents
print('\n[2] Get documents...')
docs_data, _ = get('/documents/', token)
docs = docs_data.get('data', {}).get('documents', [])
ready_docs = [d for d in docs if d['status'] == 'ready']

if not ready_docs:
    print('    No ready documents found to summarize.')
    sys.exit(1)

doc_id = ready_docs[0]['id']
print(f'    Found document: {ready_docs[0]["original_name"]}')

# Generate Concise Summary
print('\n[3] Generate Concise Summary...')
start = time.time()
summary_data, s3 = post_json('/summaries/generate', {
    'document_id': doc_id,
    'style': 'concise'
}, token)
dur = time.time() - start

print(f'    Status: {s3} (took {dur:.1f}s)')
print(f'    Success: {summary_data.get("success")}')

if s3 == 200:
    res = summary_data.get('data', {})
    print(f'    Style: {res.get("style")}')
    summary_text = res.get('summary', '')
    print(f'\n    --- SUMMARY PREVIEW ---')
    print(summary_text[:300] + ('...' if len(summary_text) > 300 else ''))
    print(f'    -----------------------')
else:
    print(f'    Error: {summary_data.get("message")}')

# Test cache
print('\n[4] Test Cache (should be fast)...')
start2 = time.time()
cache_data, s4 = post_json('/summaries/generate', {
    'document_id': doc_id,
    'style': 'concise'
}, token)
dur2 = time.time() - start2

print(f'    Status: {s4} (took {dur2:.2f}s)')
if dur2 < 1.0:
    print('    Cache hit! (Returned in < 1s)')

print('\n' + '=' * 60)
all_pass = s3 == 200 and s4 == 200 and dur2 < 1.0
print(f'SUMMARY TEST PASSED: {all_pass}')
print('=' * 60)
