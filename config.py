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
