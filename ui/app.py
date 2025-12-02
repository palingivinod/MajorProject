import tkinter as tk
import threading
import os
import tempfile
import json
from executor import gmail_sender
from utils import Logger
from audio.recorder import record_audio
from audio.transcriber import transcribe_audio
from nlu.intent_extrator import extract_intent
from executor.volume_control import change_volume as vc  
from executor import weather
#from pyttsx3 import speak_text
from executor import brightness_control as bc

class VoiceAssistantApp:
    def __init__(self):
        self.muted = False  # system mute state

        # Tkinter setup
        self.root = tk.Tk()
        self.root.title("Voice Assistant Pipeline")
        self.root.geometry("750x450")

        self.logger = Logger()

        # Transcript box
        tk.Label(self.root, text="Transcript:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.transcript_box = tk.Text(self.root, height=3, wrap="word")
        self.transcript_box.pack(fill="x")

        # Intent box
        tk.Label(self.root, text="Intent JSON:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.intent_box = tk.Text(self.root, height=6, wrap="word")
        self.intent_box.pack(fill="x")

        # Action box
        tk.Label(self.root, text="Action Taken:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.action_box = tk.Text(self.root, height=3, wrap="word")
        self.action_box.pack(fill="x")

        # Logs box
        tk.Label(self.root, text="Logs:", font=("Arial", 12, "bold")).pack(anchor="w")
        self.log_box = tk.Text(self.root, height=6, wrap="word", fg="gray")
        self.log_box.pack(fill="both", expand=True)

        # Speak button
        self.listen_btn = tk.Button(
            self.root, text="🎤 Speak", font=("Arial", 14),
            command=lambda: threading.Thread(target=self.pipeline).start()
        )
        self.listen_btn.pack(pady=10)

    def pipeline(self):
        # Create temp audio file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            audio_file = tmp.name

        self.logger.log("🎙️ Recording...")
        record_audio(audio_file)
        self.logger.log(f"✅ Saved recording: {audio_file}")

        # Transcribe
        transcript = transcribe_audio(audio_file)
        print(f"🧾 Whisper returned text: {transcript}")

        self.logger.log("📝 Transcript: " + transcript, self.transcript_box)

        # Extract intent via LLM
        response = extract_intent(transcript)

        # Convert string response to dict if necessary
        if isinstance(response, str):
            try:
                response = json.loads(response)
            except:
                response = {"intent": "other", "slots": {}}

        self.logger.log("🤖 Intent: " + str(response), self.intent_box)

        # Handle silence / mute
        if response.get("intent") == "silence":
            if not self.muted:
                self.muted = True
                self.logger.log("🔇 No speech detected. System is now muted.", self.action_box)

        # Handle unmute
        elif response.get("intent") == "unmute":
            self.muted = False
            self.logger.log("🔊 System unmuted.", self.action_box)

        # Handle volume change
        elif response.get("intent") == "change_volume":
            result = vc(response.get("slots", {}))
            self.logger.log(result, self.action_box)

        #Handle weather queries
        elif response.get("intent") == "get_weather":
            result = weather.get_weather(response.get("slots", {}))
            self.logger.log(result, self.action_box)
            #if not self.muted:
                #speak_text(result)


        # Handle mail sendings using SMTP
        elif response.get("intent") == "send_email":
            slots = response.get("slots", {})
            result = gmail_sender.send_email(slots)
            self.logger.log(result, self.action_box)
        
        # Handle brightness change
        elif response.get("intent") in ("change_brightness", "set_brightness"):
            result = bc.change_brightness(response.get("slots", {}))
            self.logger.log(result, self.action_box)

        # Handle power actions with confirmation
        elif response.get("intent") == "power_action":
            from executor import power_control as pc
            from utils.confirm import confirm_voice
            from utils.tts import speak

            slots = response.get("slots", {})
            action = slots.get("action", "lock")
            
            if action == "lock":
                prompt = "Do you want to lock the system? Say yes to confirm."
            elif action == "sleep":
                prompt = "Do you want to put the system to sleep? Say yes to confirm."
            elif action == "hibernate":
                prompt = "Do you want to hibernate the system? Say yes to confirm."
            else:
                prompt = f"Do you want to {action} the system? Say yes to confirm."

            confirmed = confirm_voice(prompt, retries=1, record_seconds=4)

            if confirmed:
                
                speak("Confirmed. Executing now.", block=False)
                result = pc.handle_power_action(slots)
                self.logger.log(result, self.action_box)
            else:
                speak("Cancelled.", block=False)
                self.logger.log("❌ Action cancelled by user.", self.action_box)

        else:
            self.logger.log(f" Action not implemented for intent: {response.get('intent')}", self.action_box)

        # Cleanup temp files
        self.cleanup_files(audio_file)

    def cleanup_files(self, audio_file):
        try:
            os.remove(audio_file)
            txt_file = audio_file + ".txt" 
            if os.path.exists(txt_file):
                os.remove(txt_file)
            self.logger.log(" Cleaned up temp files.")
        except Exception as e:
            self.logger.log(f" Cleanup failed: {e}")

    def run(self):
        self.root.mainloop()
