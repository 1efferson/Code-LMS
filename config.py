

# config.py


import os
from dotenv import load_dotenv
from datetime import timedelta

# Load environment variables from .env file
load_dotenv(dotenv_path=".env.production")


# Helper function to require environment variables
def get_env_variable(name):
    value = os.getenv(name)
    if value is None:
        raise EnvironmentError(f"Missing required environment variable: {name}")
    return value

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_SIGNUP_CODE = os.getenv('ADMIN_SIGNUP_CODE')
    
    # --- FLASK-MAIL CONFIGURATION (Secrets loaded from environment) ---
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False 
    MAIL_USE_SSL = True 
    
    # These MUST be loaded from environment variables and never hardcoded
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    # The default sender should also be customizable
    MAIL_DEFAULT_SENDER = ('CodeLMS', os.environ.get('MAIL_DEFAULT_EMAIL', 'noreply@codelms.com'))

    # Ensure required mail variables are set
    if not all([MAIL_USERNAME, MAIL_PASSWORD]):
        print("WARNING: MAIL_USERNAME and MAIL_PASSWORD are not set in environment variables!")

    PERMANENT_SESSION_LIFETIME = timedelta(minutes=2)  # 30 mins session lifetime
