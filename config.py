import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('EMAIL_USER')  # Loaded from .env
    MAIL_PASSWORD = os.environ.get('EMAIL_PASS')  # Loaded from .env
    TIME_LIMIT = 30  # Time in minutes between smoking reminders
    SLEEP_TIME = datetime.time(23, 0)  # 11:00 PM
