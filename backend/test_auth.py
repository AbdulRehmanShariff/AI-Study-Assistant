import urllib.request
import urllib.error
import json

BASE = 'http://localhost:5000/api'

def post(path, data):
    body = json.dumps(data).encode()
    req = urllib.request.Request(
        f'{BASE}{path}',
        data=body,
        headers={'Content-Type': 'application/json'},
        method='POST'
    )
    try:
        r = urllib.request.urlopen(req, timeout=5)
        return json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read()), e.code

def get(path, token=None):
    req = urllib.request.Request(f'{BASE}{path}')
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    try:
        r = urllib.request.urlopen(req, timeout=5)
        return json.loads(r.read()), r.status
    except urllib.error.HTTPError as e:
        return json.loads(e.read()), e.code

print('=' * 50)
print('AUTH API TESTS')
print('=' * 50)

# Test 1: Register
print('\n[1] POST /api/auth/register')
data, status = post('/auth/register', {
    'name': 'Test User',
    'email': 'test@studyai.com',
    'password': 'password123'
})
print(f'    Status : {status}')
print(f'    Success: {data.get("success")}')
print(f'    Message: {data.get("message")}')
token = data.get('data', {}).get('token')
user  = data.get('data', {}).get('user')
if user:
    print(f'    User   : {user.get("name")} ({user.get("email")})')
if token:
    print(f'    Token  : {token[:40]}...')

# Test 2: Duplicate registration
print('\n[2] POST /api/auth/register (duplicate email)')
data2, status2 = post('/auth/register', {
    'name': 'Another User',
    'email': 'test@studyai.com',
    'password': 'password123'
})
print(f'    Status : {status2}')
print(f'    Message: {data2.get("message")}')

# Test 3: Login
print('\n[3] POST /api/auth/login')
data3, status3 = post('/auth/login', {
    'email': 'test@studyai.com',
    'password': 'password123'
})
print(f'    Status : {status3}')
print(f'    Success: {data3.get("success")}')
login_token = data3.get('data', {}).get('token')
if login_token:
    print(f'    Token  : {login_token[:40]}...')

# Test 4: Wrong password
print('\n[4] POST /api/auth/login (wrong password)')
data4, status4 = post('/auth/login', {
    'email': 'test@studyai.com',
    'password': 'wrongpassword'
})
print(f'    Status : {status4}')
print(f'    Message: {data4.get("message")}')

# Test 5: GET /me with token
print('\n[5] GET /api/auth/me (with token)')
data5, status5 = get('/auth/me', token=login_token)
print(f'    Status : {status5}')
print(f'    User   : {data5.get("data", {}).get("user", {}).get("name")}')

# Test 6: GET /me without token
print('\n[6] GET /api/auth/me (no token)')
data6, status6 = get('/auth/me')
print(f'    Status : {status6}')
print(f'    Message: {data6.get("message")}')

print('\n' + '=' * 50)
all_pass = status in [200,201] and status2 == 400 and status3 == 200 and status4 == 401 and status5 == 200 and status6 == 401
print(f'ALL TESTS PASSED: {all_pass}')
print('=' * 50)
