from os import getenv
import pytz

NUMBER_OF_THREADS_FOR_WHISPER_MODEL = int(getenv("NUMBER_OF_THREADS_FOR_WHISPER_MODEL", 8))
MEDIA_RESPONSE_BASE_URL = "http://localhost:3000/api/"
AUDIO_SAVE_PATH = "./bot_data/audio/"
BASE_URL = getenv("WAHA_URL")
PUBLIC_BASE_URL = getenv("WAHA_PUBLIC_URL")
LLM_URL = getenv("LLM_URL")
LLM_MODEL = getenv("LLM_MODEL")
LLM_API_KEY = getenv("LLM_API_KEY")
ALLOWED_USERS = getenv('ALLOWED_USERS').split(',')
TIMEZONE = pytz.timezone(getenv("TZ"))
MAX_TOOL_CALLS = int(getenv("MAX_TOOL_CALLS", 5))
DB_PATH = getenv("DB_PATH", "./bot_data/database.db")

IMAGE_SAVE_PATH = "./bot_data/images/"


def check_config():
    if not BASE_URL:
        raise ValueError("WAHA_URL is not set in environment variables.")
    if not PUBLIC_BASE_URL:
        raise ValueError("WAHA_PUBLIC_URL is not set in environment variables.")
    if not LLM_URL:
        raise ValueError("LLM_URL is not set in environment variables.")
    if not LLM_MODEL:
        raise ValueError("LLM_MODEL is not set in environment variables.")
    if not ALLOWED_USERS:
        raise ValueError("ALLOWED_USERS is not set in environment variables.")
    if not TIMEZONE:
        raise ValueError("TZ is not set in environment variables.")