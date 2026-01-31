
# config.py

import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent

ENV = os.getenv('FLASK_ENV', "development")

if ENV == 'development':
    load_dotenv(BASE_DIR / '.env.development')
    print(" Development Mode: Using SQLite (Fast!)")
else:
    load_dotenv(BASE_DIR / '.env.production')
    print("Production Mode: Using PostgreSQL")


class Config:
    # Environment
    ENV = ENV 
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY')
    ADMIN_SIGNUP_CODE = os.getenv('ADMIN_SIGNUP_CODE')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SQLAlchemy engine options (only for production PostgreSQL)
    if ENV == 'production':
        SQLALCHEMY_ENGINE_OPTIONS = {
            "pool_size": 10,
            "max_overflow": 5,
            "pool_timeout": 30,
            "pool_recycle": 1800,
            "pool_pre_ping": True,
        }
    else:
        # SQLite doesn't need connection pooling
        SQLALCHEMY_ENGINE_OPTIONS = {}
    
    # Flask-Mail Configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False 
    MAIL_USE_SSL = True 
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = ('CodeLMS', os.getenv('MAIL_DEFAULT_EMAIL', 'noreply@codelms.com'))
    
    # Warn if mail not configured (optional in dev)
    if ENV == 'production' and not all([MAIL_USERNAME, MAIL_PASSWORD]):
        print("WARNING: MAIL_USERNAME and MAIL_PASSWORD not set!")
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # Cache
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 300

    # File Uploads
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'lms/courses/static/uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB 
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    # Storage configuration
    STORAGE_BACKEND = os.getenv('STORAGE_BACKEND', 'local') 
    
    # Local storage settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'lms/courses/static/uploads')
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Cloudinary settings
    CLOUDINARY_CLOUD_NAME = os.getenv('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY = os.getenv('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.getenv('CLOUDINARY_API_SECRET')