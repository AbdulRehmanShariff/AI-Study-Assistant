import urllib.request
import urllib.error
import json
import sys

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
print('RAG PIPELINE END-TO-END TEST')
print('=' * 60)

# Login
print('\n[1] Login...')
login_data, _ = post_json('/auth/login', {'email': 'test@studyai.com', 'password': 'password123'})
token = login_data.get('data', {}).get('token')
print(f'    Token: {"OK" if token else "FAILED"}')
if not token: sys.exit(1)

# Check LLM status
print('\n[2] LLM Status...')
status_data, s2 = get('/chat/status')
llm = status_data.get('data', {})
print(f'    Configured: {llm.get("configured")}')
print(f'    Model     : {llm.get("model")}')

# Ask a question (uses existing documents in DB)
print('\n[3] Ask RAG question...')
q_data, s3 = post_json('/chat/ask', {
    'question': 'What is a transformer and how does self-attention work?',
    'top_k': 3,
}, token)
print(f'    Status: {s3}')
print(f'    Success: {q_data.get("success")}')

result = q_data.get('data', {})
answer  = result.get('answer', '')
sources = result.get('sources', [])

if answer:
    print(f'\n    ANSWER (first 400 chars):')
    print(f'    {answer[:400]}')
    print(f'\n    Sources used: {len(sources)}')
    for i, s in enumerate(sources[:3]):
        print(f'      [{s.get("score", 0):.3f}] {s.get("text", "")[:60]}...')
else:
    msg = q_data.get('message', 'No answer')
    print(f'    Message: {msg}')

# Check chat history
print('\n[4] Chat history...')
hist_data, s4 = get('/chat/history', token)
msgs = hist_data.get('data', {}).get('messages', [])
print(f'    Status: {s4}')
print(f'    Messages in history: {len(msgs)}')

print('\n' + '=' * 60)
all_pass = s2 == 200 and s3 == 200 and len(answer) > 50
print(f'RAG TEST PASSED: {all_pass}')
print('=' * 60)
