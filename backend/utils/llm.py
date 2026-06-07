import time
from google import genai
from google.genai import types
from config.settings import Config


class GeminiLLM:
    """Wrapper around Google Gemini API for text generation.

    Uses gemini-2.0-flash-lite for fast, high-quality responses.
    Singleton client — initialized once per process.
    """

    _client = None
    MODEL = 'gemini-flash-latest'
    FALLBACK_MODELS = ['gemini-2.5-flash-lite', 'gemini-flash-lite-latest']

    @classmethod
    def _get_client(cls):
        """Get or create the Gemini client."""
        if cls._client is None:
            api_key = Config.GEMINI_API_KEY
            if not api_key or api_key == 'your-gemini-api-key-here':
                raise ValueError(
                    'GEMINI_API_KEY is not set. '
                    'Add your key to backend/.env as: GEMINI_API_KEY=your_key_here'
                )
            cls._client = genai.Client(api_key=api_key)
        return cls._client

    @classmethod
    def generate(cls, prompt, system_instruction=None, temperature=0.3, max_tokens=8192):
        """Generate a response, trying primary model then fallbacks."""
        client = cls._get_client()

        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            system_instruction=system_instruction or (
                'You are an expert AI Study Assistant. '
                'Answer questions accurately based on the provided study material. '
                'Provide highly detailed, in-depth, and comprehensive educational explanations. '
                'If the context does not contain enough information, say so honestly.'
            ),
        )

        models_to_try = [cls.MODEL] + cls.FALLBACK_MODELS
        last_error = None

        for model in models_to_try:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=config,
                )
                return response.text
            except Exception as e:
                err_str = str(e)
                last_error = e
                # 429 or 503: rate limited or overloaded — wait and retry with same model once
                if '429' in err_str or '503' in err_str:
                    import re
                    delay_match = re.search(r'retry.*?(\d+)', err_str, re.IGNORECASE)
                    delay = int(delay_match.group(1)) if delay_match else 5
                    delay = min(delay, 20)  # cap at 20s
                    print(f'[INFO] API overloaded/rate limited on {model}, waiting {delay}s...')
                    time.sleep(delay)
                    try:
                        response = client.models.generate_content(
                            model=model, contents=prompt, config=config,
                        )
                        return response.text
                    except Exception as retry_err:
                        last_error = retry_err
                        print(f'[WARN] Retry failed on {model}: {retry_err}')
                # 404: model not found — try next
                elif '404' in err_str:
                    print(f'[WARN] Model {model} not found, trying next...')
                    continue
                else:
                    raise RuntimeError(f'Gemini generation failed: {e}')

        raise RuntimeError(
            f'All Gemini models exhausted. Last error: {last_error}. '
            'Please check your API key quota at https://ai.dev/rate-limit'
        )

    @classmethod
    def is_configured(cls):
        """Check if the API key is properly configured."""
        key = Config.GEMINI_API_KEY
        return bool(key and key != 'your-gemini-api-key-here')
