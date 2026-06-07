import sys
sys.path.insert(0, '.')
from config.settings import Config
from google import genai

client = genai.Client(api_key=Config.GEMINI_API_KEY)

print("Available models:")
for m in client.models.list():
    print(f"  {m.name}  |  {getattr(m, 'display_name', '')}")
