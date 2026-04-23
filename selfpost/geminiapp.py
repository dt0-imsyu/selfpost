import os
from google import genai
from apikeys import geminikey

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", geminikey).strip()
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY не задан. Укажите ключ Gemini в apikeys.py")

client = genai.Client(api_key=GEMINI_API_KEY)

MODEL_NAME = "gemini-2.5-flash-lite"
print(f"[LLM/Gemini] client initialized. model={MODEL_NAME}")


def aireq(req):
    req = str(req)
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=req,
    )
    text = response.text or ""
    print(f"[LLM/Gemini] model used: {MODEL_NAME}")
    return text.strip()
