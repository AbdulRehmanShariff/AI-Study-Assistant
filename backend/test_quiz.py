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
print('QUIZ GENERATION API TEST')
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
    print('    No ready documents found.')
    sys.exit(1)

doc_id = ready_docs[0]['id']
print(f'    Found document: {ready_docs[0]["original_name"]}')

# Generate Quiz
print('\n[3] Generate 3-Question Quiz...')
start = time.time()
quiz_data, s3 = post_json('/quiz/generate', {
    'document_id': doc_id,
    'count': 3
}, token)
dur = time.time() - start

print(f'    Status: {s3} (took {dur:.1f}s)')
print(f'    Success: {quiz_data.get("success")}')

if s3 == 200:
    quiz = quiz_data.get('data', {}).get('quiz', {})
    questions = quiz.get('questions', [])
    print(f'    Generated {len(questions)} questions')
    
    if len(questions) > 0:
        q = questions[0]
        print(f'\n    --- PREVIEW Q1 ---')
        print(f'    Q: {q.get("question")}')
        for i, opt in enumerate(q.get('options', [])):
            mark = '*' if i == q.get('correct_index') else ' '
            print(f'    [{mark}] {chr(65+i)}. {opt}')
        print(f'    Explanation: {q.get("explanation")}')
        print(f'    ------------------')
else:
    print(f'    Error: {quiz_data.get("message")}')

# Test get existing
print('\n[4] Test fetching existing quiz...')
start2 = time.time()
fetch_data, s4 = get(f'/quiz/{doc_id}', token)
dur2 = time.time() - start2

print(f'    Status: {s4} (took {dur2:.2f}s)')
if dur2 < 1.0:
    print('    Cache hit! (Returned in < 1s)')

print('\n' + '=' * 60)
all_pass = s3 == 200 and s4 == 200 and dur2 < 1.0
print(f'QUIZ TEST PASSED: {all_pass}')
print('=' * 60)
