import sounddevice as sd
import numpy as np
import wave

def record_audio(filename="audio.wav", duration=8, fs=16000):
    print("🎙️ Recording...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype="int16")
    sd.wait()

    wf = wave.open(filename, "wb")
    wf.setnchannels(1)
    wf.setsampwidth(2)  # 16-bit
    wf.setframerate(fs)
    wf.writeframes(recording.tobytes())
    wf.close()

    print("✅ Saved recording:", filename)
    return filename
