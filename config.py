import os
from dotenv import load_dotenv

# Load .env file from the same directory as this config.py file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY","fallback_secret")
    SQLALCHEMY_DATABASE_URI = "sqlite:///mindease.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
