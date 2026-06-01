import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def get_required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Set the {name} environment variable.")
    return value


BOT_TOKEN = get_required_env("BOT_TOKEN")
GEMINI_API_KEY = get_required_env("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite").strip()
DATA_FILE = Path(os.getenv("SELFPOST_DATA_FILE", "bot_data.json"))
