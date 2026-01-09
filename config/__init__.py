from .settings import WHISPER_BIN, WHISPER_MODEL, OLLAMA_MODEL
import os
import json

CRED_PATH = os.path.join(os.path.dirname(__file__), "credentials.json")
GOOGLE_CREDENTIALS_PATH = os.path.join(os.path.dirname(__file__), "googlecredentials.json")

with open(CRED_PATH, "r") as f:
    creds = json.load(f)

EMAIL = creds.get("email")
EMAIL_PASSWORD = creds.get("email_password")

__all__ = ["WHISPER_BIN", "WHISPER_MODEL", "OLLAMA_MODEL","EMAIL", "EMAIL_PASSWORD"]
