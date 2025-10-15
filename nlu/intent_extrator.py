import subprocess
import json
import config.settings as cfg
from nlu.prompts import INTENT_PROMPT

def extract_intent(transcript: str):
    """
    Extract intent from transcript using local LLaMA/Mistral model via Ollama.
    Returns a dict with 'intent' and 'slots'.
    """
    # Build prompt
    prompt = INTENT_PROMPT + transcript + "\n\nReturn JSON only with keys 'intent' and optional 'slots'."

    try:
        # Call Ollama locally with your LLaMA/Mistral model
        result = subprocess.run(
            ["ollama", "run", cfg.OLLAMA_MODEL],  
            input=prompt.encode(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True
        )

        text = result.stdout.decode().strip()

        parsed = json.loads(text)

    except subprocess.CalledProcessError as e:
        print(f"❌ Ollama call failed: {e.stderr.decode().strip()}")
        parsed = {"intent": "other", "slots": {}}
    except json.JSONDecodeError:
        print(f"❌ JSON parsing failed. LLM output: {text}")
        parsed = {"intent": "other", "slots": {}}
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        parsed = {"intent": "other", "slots": {}}

    return parsed
