# utils/confirm.py
import tempfile
import time
from utils.tts import speak
from audio.recorder import record_audio
from audio.transcriber import transcribe_audio

YES_PHRASES = {"yes", "yeah", "yup", "confirm", "sure", "okay", "ok", "affirmative", "proceed"}
NO_PHRASES = {"no", "nope", "nah", "cancel", "stop", "negative", "don't", "do not", "not now"}

def _normalize_text(t: str):
    if not t:
        return ""
    return t.strip().lower()

def confirm_voice(prompt: str, retries: int = 1, record_seconds: int = 4):
    """
    Speak `prompt` and listen for a yes/no response.
    Returns True if confirmed, False if denied or unclear after retries.
    - retries: how many extra tries to re-prompt
    - record_seconds: how long to record; adapt if your recorder supports duration
    """
    for attempt in range(retries + 1):
        # Speak prompt (blocking)
        speak(prompt, block=True)

        # Create temp file and record
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            audio_path = tmp.name

        # If your recorder supports duration, use it; otherwise it should record until silence or fixed time
        try:
            # If record_audio supports duration, change call accordingly:
            # record_audio(audio_path, duration=record_seconds)
            record_audio(audio_path)
            # small wait to ensure file flush
            time.sleep(0.2)
            transcript = transcribe_audio(audio_path)
        except Exception:
            transcript = ""

        text = _normalize_text(transcript)
        tokens = set(word.strip(".,!?") for word in text.split())

        # check explicit yes/no
        if tokens & YES_PHRASES:
            return True
        if tokens & NO_PHRASES:
            return False

        # prefixes fallback
        if text.startswith(("yes", "yeah", "ok", "okay")):
            return True
        if text.startswith(("no", "nah", "cancel")):
            return False

        # unclear -> re-prompt if retries remain
        if attempt < retries:
            speak("I didn't catch that. Please say yes or no.", block=True)

    # default: not confirmed
    return False
