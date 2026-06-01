from google import genai

from config import GEMINI_API_KEY, GEMINI_MODEL

client = genai.Client(api_key=GEMINI_API_KEY)

print(f"[LLM/Gemini] client initialized. model={GEMINI_MODEL}")


def aireq(req: str) -> str:
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=str(req),
    )
    text = response.text or ""
    return text.strip()
