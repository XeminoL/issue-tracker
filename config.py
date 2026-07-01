import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-in-production')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///issue_tracker.db')

    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DEBUG = os.getenv('FLASK_ENV', 'development') == 'development'

    # CSRF protection (Flask-WTF). Disabled automatically under TESTING so the
    # API test client does not need to fetch a token for every request.
    WTF_CSRF_ENABLED = os.getenv('WTF_CSRF_ENABLED', 'true').lower() == 'true'
    WTF_CSRF_TIME_LIMIT = None  # token valid for the whole session
