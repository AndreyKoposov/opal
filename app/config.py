from os import getenv

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
