import subprocess
import config.settings as cfg
import os

def transcribe_audio(audio_file):
    cmd = [
        cfg.WHISPER_BIN,
        "-m", cfg.WHISPER_MODEL,
        "-f", audio_file,
        "-otxt"
    ]
    
    subprocess.run(cmd, check=True)

    output_file = audio_file + ".txt"

    with open(output_file, "r", encoding="utf-8") as f:
        text = f.read().strip()

    return text
