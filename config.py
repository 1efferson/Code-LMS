

# config.py


import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Helper function to require environment variables
def get_env_variable(name):
    value = os.getenv(name)
    if value is None:
        raise EnvironmentError(f"Missing required environment variable: {name}")
    return value

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    # Fallback to the instance sqlite file if DATABASE_URL is not set
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///instance/lms.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMIN_SIGNUP_CODE = os.getenv('ADMIN_SIGNUP_CODE')