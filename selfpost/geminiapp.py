import os
from google import genai
from apikeys import geminikey

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", geminikey).strip()
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY не задан. Укажите ключ Gemini в apikeys.py или env.")

client = genai.Client(api_key=GEMINI_API_KEY)

# Можно переопределить через переменную окружения GEMINI_MODEL.
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
FALLBACK_MODELS = ("gemini-2.0-flash-lite", "gemini-2.5-flash")


def aireq(req):
    topic = str(req).strip() or "без темы"
    return (
        f"Тема: {topic}\n\n"
        "Это временная заглушка вместо генерации ИИ.\n"
        "Здесь будет автоматически сгенерированный пост, когда подключим финальный провайдер.\n\n"
        "Короткая структура поста:\n"
        "1) Вступление по теме\n"
        "2) Основная польза/мысль\n"
        "3) Призыв к действию для подписчиков"
    )
