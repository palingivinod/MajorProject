# import subprocess
# import json
# import config.settings as cfg
# from nlu.prompts import INTENT_PROMPT

# def extract_intent(transcript: str):
#     """
#     Extract intent from transcript using local LLaMA/Mistral model via Ollama.
#     Returns a dict with 'intent' and 'slots'.
#     """
#     # Build prompt
#     prompt = INTENT_PROMPT + transcript + "\n\nReturn JSON only with keys 'intent' and optional 'slots'."

#     try:
#         # Call Ollama locally with your LLaMA/Mistral model
#         result = subprocess.run(
#             ["ollama", "run", cfg.OLLAMA_MODEL],  
#             input=prompt.encode(),
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             check=True
#         )

#         text = result.stdout.decode().strip()

#         parsed = json.loads(text)

#     except subprocess.CalledProcessError as e:
#         print(f"❌ Ollama call failed: {e.stderr.decode().strip()}")
#         parsed = {"intent": "other", "slots": {}}
#     except json.JSONDecodeError:
#         print(f"❌ JSON parsing failed. LLM output: {text}")
#         parsed = {"intent": "other", "slots": {}}
#     except Exception as e:
#         print(f"❌ Unexpected error: {e}")
#         parsed = {"intent": "other", "slots": {}}

#     return parsed


import subprocess
import json
import socket
import requests
import config.settings as cfg
from nlu.prompts import INTENT_PROMPT

# checking for internet connectivity
def is_internet_available(host="8.8.8.8", port=53, timeout=2):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False

# extract intent using Groq API
def extract_intent_groq(prompt: str):
    headers = {
        "Authorization": f"Bearer {cfg.GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": cfg.GROQ_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are an intent extractor. Return ONLY valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0
    }

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=15
    )

    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"].strip()

    return json.loads(content)

# Extract intent using local ollama

def extract_intent_ollama(prompt: str):
    result = subprocess.run(
        ["ollama", "run", cfg.OLLAMA_MODEL],
        input=prompt.encode(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    text = result.stdout.decode().strip()
    return json.loads(text)

# main functionality

def extract_intent(transcript: str):
    """
    Hybrid intent extraction:
    - Uses Groq if internet is available
    - Falls back to local Ollama if offline or Groq fails
    """

    prompt = (
        INTENT_PROMPT
        + transcript
        + "\n\nReturn JSON only with keys 'intent' and optional 'slots'."
    )

    try:
        # Prefer online LLM if internet exists
        if is_internet_available():
            try:
                return extract_intent_groq(prompt)
            except Exception as e:
                print(" Groq failed, switching to local LLM:", e)

        # Fallback to local Ollama
        return extract_intent_ollama(prompt)

    except json.JSONDecodeError as e:
        print(" JSON parsing failed:", e)
        return {"intent": "other", "slots": {}}

    except Exception as e:
        print(" Unexpected intent extraction error:", e)
        return {"intent": "other", "slots": {}}
