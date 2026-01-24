
# config.py

import os
from dotenv import load_dotenv
from datetime import timedelta

# Auto-detect environment and load appropriate .env file
env = os.getenv('FLASK_ENV', 'production')

if env == 'development':
    load_dotenv('.env.development')
    print(" Development Mode: Using SQLite (Fast!)")
else:
    load_dotenv('.env.production')
    print("Production Mode: Using PostgreSQL")


class Config:
    # Environment
    ENV = os.getenv('FLASK_ENV', 'production')
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