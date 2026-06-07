import urllib.request
import urllib.error
import json
import io
import os

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

def delete(path, token=None):
    req = urllib.request.Request(f'{BASE}{path}', method='DELETE')
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    try:
        r = urllib.request.urlopen(req, timeout=10)
        return json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read()), e.code

def post_multipart(path, filename, file_content, content_type, token=None):
    """Simple multipart form upload."""
    boundary = b'----TestBoundary7329847'
    body = (
        b'--' + boundary + b'\r\n'
        b'Content-Disposition: form-data; name="file"; filename="' + filename.encode() + b'"\r\n'
        b'Content-Type: ' + content_type.encode() + b'\r\n\r\n'
        + file_content + b'\r\n'
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
print('DOCUMENT API TESTS')
print('=' * 55)

# Get a token first (login as test user from phase 5)
print('\n[0] Login to get token...')
login_data, _ = post_json('/auth/login', {'email': 'test@studyai.com', 'password': 'password123'})
token = login_data.get('data', {}).get('token')
print(f'    Token: {"OK" if token else "FAILED"}')

# Test 1: Upload TXT
print('\n[1] POST /api/documents/upload (TXT)')
txt_content = b'Chapter 1: Introduction to Machine Learning\n\nMachine learning is a subset of artificial intelligence. It allows computers to learn from data.\n\nChapter 2: Supervised Learning\n\nSupervised learning uses labeled training data to train models.'
data1, s1 = post_multipart('/documents/upload', 'test_notes.txt', txt_content, 'text/plain', token)
print(f'    Status : {s1}')
print(f'    Success: {data1.get("success")}')
doc_txt = data1.get('data', {}).get('document', {})
if doc_txt:
    print(f'    File   : {doc_txt.get("original_name")}')
    print(f'    Words  : {doc_txt.get("word_count")}')
    print(f'    Status : {doc_txt.get("status")}')
txt_id = doc_txt.get('id')

# Test 2: List documents
print('\n[2] GET /api/documents/')
data2, s2 = get('/documents/', token)
print(f'    Status : {s2}')
print(f'    Count  : {data2.get("data", {}).get("count", 0)}')

# Test 3: Get single document
if txt_id:
    print(f'\n[3] GET /api/documents/{txt_id[:8]}...')
    data3, s3 = get(f'/documents/{txt_id}', token)
    print(f'    Status : {s3}')
    print(f'    Name   : {data3.get("data", {}).get("document", {}).get("original_name")}')

# Test 4: Upload without auth
print('\n[4] POST /api/documents/upload (no auth)')
data4, s4 = post_multipart('/documents/upload', 'test.txt', b'hello', 'text/plain')
print(f'    Status : {s4}')
print(f'    Message: {data4.get("message")}')

# Test 5: Delete the uploaded document
if txt_id:
    print(f'\n[5] DELETE /api/documents/{txt_id[:8]}...')
    data5, s5 = delete(f'/documents/{txt_id}', token)
    print(f'    Status : {s5}')
    print(f'    Message: {data5.get("message")}')

# Test 6: Wrong file type
print('\n[6] POST /api/documents/upload (invalid file type)')
data6, s6 = post_multipart('/documents/upload', 'image.jpg', b'fake image', 'image/jpeg', token)
print(f'    Status : {s6}')
print(f'    Message: {data6.get("message")}')

print('\n' + '=' * 55)
all_pass = s1 == 201 and s2 == 200 and s4 == 401 and s5 == 200 and s6 == 400
print(f'ALL TESTS PASSED: {all_pass}')
print('=' * 55)
