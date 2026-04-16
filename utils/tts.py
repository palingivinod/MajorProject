# utils/tts.py
import threading
import traceback
import subprocess

# Try to import pyttsx3 + COM things (Windows). If unavailable, fallback to PowerShell TTS.
try:
    import pyttsx3
    import pythoncom
    _HAVE_PYTTX3 = True
except Exception:
    _HAVE_PYTTX3 = False

def _sapi_speak(text: str):
    """
    Initialize COM in this thread and use pyttsx3 (SAPI).
    Should be called from the thread that will run TTS.
    """
    try:
        pythoncom.CoInitialize()
        engine = pyttsx3.init(driverName="sapi5")
        # optional tuning
        rate = engine.getProperty("rate")
        engine.setProperty("rate", int(rate * 0.95))
        engine.say(text)
        engine.runAndWait()
        engine.stop()
    except Exception:
        traceback.print_exc()
    finally:
        try:
            pythoncom.CoUninitialize()
        except Exception:
            pass

def _powershell_speak(text: str):
    """
    Fallback TTS using PowerShell System.Speech (offline).
    """
    safe = text.replace("'", "''")  # escape single quotes for PS
    ps = f"Add-Type -AssemblyName System.speech; $s=new-object System.Speech.Synthesis.SpeechSynthesizer; $s.Speak('{safe}');"
    subprocess.run(["powershell", "-Command", ps], check=False)

def speak(text: str, block: bool = True):
    """
    Speak the provided text offline.
    - block=True: wait until finished.
    - block=False: speak in background thread (non-blocking).
    """
    if not text:
        return

    # Prefer pyttsx3 + SAPI on Windows for best quality
    if _HAVE_PYTTX3:
        if block:
            _sapi_speak(text)
            return
        else:
            t = threading.Thread(target=_sapi_speak, args=(text,), daemon=True)
            t.start()
            return

    # Fallback to PowerShell
    if block:
        _powershell_speak(text)
    else:
        threading.Thread(target=_powershell_speak, args=(text,), daemon=True).start()
