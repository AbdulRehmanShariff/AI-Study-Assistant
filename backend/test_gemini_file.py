import os
import sys
import tempfile

sys.path.insert(0, 'C:\\AI Study Assistant\\backend')
from utils.llm import GeminiLLM

client = GeminiLLM._get_client()

# create a dummy pdf
path = 'test.txt'
with open(path, 'w') as f:
    f.write('Hello OCR')

print(dir(client))
try:
    if hasattr(client, 'files'):
        print('Files API:', dir(client.files))
except Exception as e:
    print(e)
