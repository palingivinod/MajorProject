# Path to whisper.cpp executable
WHISPER_BIN = "Release/whisper-cli.exe"

# Path to whisper model
WHISPER_MODEL = "Release/ggml-base.en.bin"

GROQ_API_KEY = "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"
GROQ_MODEL = "llama-3.1-8b-instant"
 
#llama3-70b-8192

OLLAMA_BIN = "C:/Users/vinod/AppData/Local/Programs/Ollama/ollama.exe"
OLLAMA_MODEL = "llama3"   # or "llama3"

OLLAMA_TIMEOUT = 8

import os

BASE_DIR = os.path.dirname(__file__)

GOOGLE_CREDENTIALS_PATH = os.path.join(BASE_DIR, "googlecredentials.json")
GOOGLE_TOKEN_PATH = os.path.join(BASE_DIR, "token.json")

GOOGLE_SCOPES = ["https://www.googleapis.com/auth/calendar"]
