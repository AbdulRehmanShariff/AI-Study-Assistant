import os
from google import genai
from config.settings import Config

api_key = Config.GEMINI_API_KEY
client = genai.Client(api_key=api_key)

models_to_test = [
    'gemini-flash-latest',
    'gemini-flash-lite-latest',
    'gemini-2.5-flash-lite'
]

for m in models_to_test:
    try:
        print(f"Testing {m}...")
        response = client.models.generate_content(
            model=m,
            contents='Hello'
        )
        print(f"SUCCESS: {m}:", response.text)
    except Exception as e:
        print(f"FAILED: {m}:", e)
