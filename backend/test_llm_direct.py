import sys
sys.path.insert(0, '.')
from utils.llm import GeminiLLM

try:
    print("Testing Gemini directly...")
    answer = GeminiLLM.generate(
        prompt="What is a transformer?",
        system_instruction="You are a helpful AI.",
        max_tokens=100
    )
    print("SUCCESS:")
    print(answer)
except Exception as e:
    print("ERROR:")
    print(str(e))
