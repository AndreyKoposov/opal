from os import getenv
from pathlib import Path


BASE_DIR = Path(__file__).parent
STATIC_DIR = BASE_DIR / "static"
UPLOAD_DIR = BASE_DIR.parent / "uploads"

MAX_FILE_SIZE = 20 * 1024 * 1024   # 20 МБ
ALLOWED_EXTENSIONS = {".pdf"}

AI_ENGINE = getenv('AI_ENGINE', default='')
AI_MODEL = getenv('AI_MODEL', '')
AI_API_KEY = getenv('AI_API_KEY', '')
AI_TEMP = getenv('AI_TEMP', '')

DB_NAME = getenv('DB_NAME', '')
DB_USER = getenv('DB_USER', '')
DB_PSWRD = getenv('DB_PSWRD', '')
DB_HOST = getenv('DB_HOST', '')
DB_PORT = getenv('DB_PORT', '')

DEBUG = getenv('DEBUG')
