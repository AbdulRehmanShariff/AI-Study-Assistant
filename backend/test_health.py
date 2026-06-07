import urllib.request
import json

try:
    r = urllib.request.urlopen('http://localhost:5000/api/health', timeout=5)
    data = json.loads(r.read())
    print("STATUS: OK")
    print("Response:", json.dumps(data, indent=2))
except Exception as e:
    print("STATUS: FAILED")
    print("Error:", e)
