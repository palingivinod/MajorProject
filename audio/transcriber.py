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

    # Whisper saves as <audio_file>.txt, not replaced
    output_file = audio_file + ".txt"

    with open(output_file, "r", encoding="utf-8") as f:
        text = f.read().strip()

    # # (Optional) Auto-clean temp files
    # try:
    #     os.remove(audio_file)       # delete .wav
    #     os.remove(output_file)      # delete .wav.txt
    # except FileNotFoundError:
    #     pass

    return text
