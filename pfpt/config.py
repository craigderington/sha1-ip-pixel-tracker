import os


CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
MONGO_SERVER = '172.26.13.37'
MONGO_DB = 'earl-pixel-tracker'
SECRET_KEY = os.urandom(64)
