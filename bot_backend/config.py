from os import getenv
import pytz

NUMBER_OF_THREADS_FOR_WHISPER_MODEL = int(getenv("NUMBER_OF_THREADS_FOR_WHISPER_MODEL", 16))
MEDIA_RESPONSE_BASE_URL = "http://localhost:3000/api/"
AUDIO_SAVE_PATH = "./bot_data/audio/"
BASE_URL = getenv("WAHA_URL")
PUBLIC_BASE_URL = getenv("WAHA_PUBLIC_URL")
LLM_URL = getenv("LLM_URL")
LLM_MODEL = getenv("LLM_MODEL")
ALLOWED_USERS = getenv('ALLOWED_USERS').split(',')


TIMEZONE = pytz.timezone(getenv("TZ"))

IMAGE_SAVE_PATH = "./bot_data/images/"