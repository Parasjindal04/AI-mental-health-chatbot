import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY","fallback_secret")
    SQLALCHEMY_DATABASE_URI = "sqlite:///mindease.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
