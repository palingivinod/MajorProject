import tkinter as tk
import threading
import os
import tempfile
import json

from utils import Logger
from audio.recorder import record_audio
from audio.transcriber import transcribe_audio
from nlu.intent_extrator import extract_intent
from executor import calendar_api as cal
from executor import weather
from executor import brightness_control as bc
from executor import volume_control as vcc
from executor.volume_control import change_volume as vc
from executor import calendar_api as cal
from executor import music_control as mc

class VoiceAssistantApp:
    def __init__(self):
        self.muted = False 

        # Tkinter setup
        self.root = tk.Tk()
        self.root.title("Voice Assistant Pipeline")
        self.root.geometry("750x520")

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
            self.root,
            text=" Speak",
            font=("Arial", 14),
            command=lambda: threading.Thread(target=self.pipeline, daemon=True).start()
        )
        self.listen_btn.pack(pady=8)

        tk.Label(self.root, text="Chat Input:", font=("Arial", 12, "bold")).pack(anchor="w")

        self.chat_entry = tk.Entry(self.root, font=("Arial", 12))
        self.chat_entry.pack(fill="x", padx=5)

        self.send_btn = tk.Button(
            self.root,
            text="💬 Send",
            font=("Arial", 12),
            command=lambda: threading.Thread(
                target=self.process_text_input,
                daemon=True
            ).start()
        )
        self.send_btn.pack(pady=6)

#voice handling pipeline
    def pipeline(self):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            audio_file = tmp.name

        try:
            self.logger.log(" Recording...", self.log_box)
            record_audio(audio_file)
            self.logger.log(f"Saved recording: {audio_file}", self.log_box)

            transcript = transcribe_audio(audio_file).strip()
            print(f" Whisper returned text: {transcript}")

            self.logger.log("Transcript: " + transcript, self.transcript_box)

            # SAME handler used by chat
            self.handle_intent_and_execute(transcript)

        except Exception as e:
            self.logger.log(f" Pipeline error: {e}", self.log_box)

        finally:
            self.cleanup_files(audio_file)

    def process_text_input(self):
        transcript = self.chat_entry.get().strip()
        if not transcript:
            return

        self.chat_entry.delete(0, tk.END)
        self.logger.log(" Transcript (Text): " + transcript, self.transcript_box)

        self.handle_intent_and_execute(transcript)

    def handle_intent_and_execute(self, transcript: str):
        response = extract_intent(transcript)

        if isinstance(response, str):
            try:
                response = json.loads(response)
            except:
                response = {"intent": "other", "slots": {}}

        intent = response.get("intent")
        slots = response.get("slots", {}) or {}

        self.logger.log(" Intent: " + str(response), self.intent_box)

        #intent handling

        if intent == "change_volume":
            if any(k in slots for k in ("percent", "value", "level", "amount")):
                result = vcc.set_volume_percent(slots)
            else:
                result = vc(slots)
            self.logger.log(result, self.action_box)

        elif intent == "get_weather":
            result = weather.get_weather(slots)
            self.logger.log(result, self.action_box)

        elif intent == "send_email":
            from executor import gmail_sender
            result = gmail_sender.send_email(slots)
            self.logger.log(result, self.action_box)

        elif intent in ("change_brightness", "set_brightness"):
            result = bc.change_brightness(slots)
            self.logger.log(result, self.action_box)

        elif intent == "power_action":
            from executor import power_control as pc
            from utils.confirm import confirm_voice
            from utils.tts import speak

            action = slots.get("action", "lock")
            prompt = f"Do you want to {action} the system? Say yes to confirm."

            confirmed = confirm_voice(prompt, retries=1, record_seconds=4)

            if confirmed:
                speak("Confirmed. Executing now.", block=False)
                result = pc.handle_power_action(slots)
                self.logger.log(result, self.action_box)
            else:
                speak("Cancelled.", block=False)
                self.logger.log(" Action cancelled.", self.action_box)
        
        elif response.get("intent") == "create_event":
            result = cal.create_event(response.get("slots", {}))
            self.logger.log(result, self.action_box)

        elif intent == "music_control":
            
            action = slots.get("action")

            if action == "play_pause":
                result = mc.play_pause()
            elif action == "next":
                result = mc.next_track()
            elif action == "previous":
                result = mc.previous_track()
            else:
                result = "Unknown music action."

            self.logger.log(result, self.action_box)


        else:
            self.logger.log(
                f"Action not implemented for intent: {intent}",
                self.action_box
            )

   #clean files and data
    def cleanup_files(self, audio_file):
        try:
            if os.path.exists(audio_file):
                os.remove(audio_file)

            txt_file = audio_file + ".txt"
            if os.path.exists(txt_file):
                os.remove(txt_file)

            self.logger.log(" Cleaned up temp files.", self.log_box)

        except Exception as e:
            self.logger.log(f"Cleanup failed: {e}", self.log_box)

    def run(self):
        self.root.mainloop()


# import tkinter as tk
# import threading
# import os
# import tempfile
# import json

# from utils import Logger
# from audio.recorder import record_audio
# from audio.transcriber import transcribe_audio
# from nlu.intent_extrator import extract_intent
# from executor import calendar_api as cal
# from executor import weather
# from executor import brightness_control as bc
# from executor import volume_control as vcc
# from executor.volume_control import change_volume as vc


# # ---------------- UI THEME ----------------
# BG_COLOR = "#1e1e1e"
# CARD_COLOR = "#2a2a2a"
# TEXT_COLOR = "#eaeaea"
# SUBTEXT_COLOR = "#9cdcfe"
# BTN_COLOR = "#0e639c"
# BTN_HOVER = "#1177bb"
# ENTRY_BG = "#3c3c3c"


# class VoiceAssistantApp:
#     def __init__(self):
#         self.muted = False

#         self.root = tk.Tk()
#         self.root.title("Offline AI Assistant")
#         self.root.geometry("780x560")
#         self.root.configure(bg=BG_COLOR)

#         self.logger = Logger()

#         # --------- CARD FRAME ----------
#         container = tk.Frame(self.root, bg=BG_COLOR)
#         container.pack(fill="both", expand=True, padx=12, pady=10)

#         # ---------- TRANSCRIPT ----------
#         self._section(container, "Transcript")
#         self.transcript_box = self._text(container, height=3)

#         # ---------- INTENT ----------
#         self._section(container, "Intent (LLM Output)")
#         self.intent_box = self._text(container, height=6)

#         # ---------- ACTION ----------
#         self._section(container, "Action Taken")
#         self.action_box = self._text(container, height=3)

#         # ---------- LOGS ----------
#         self._section(container, "Logs")
#         self.log_box = self._text(container, height=6, fg="#7fd7ff")

#         # ---------- BUTTONS ----------
#         btn_frame = tk.Frame(container, bg=BG_COLOR)
#         btn_frame.pack(pady=8)

#         self.listen_btn = self._button(
#             btn_frame,
#             "🎤 Speak",
#             lambda: threading.Thread(target=self.pipeline, daemon=True).start()
#         )
#         self.listen_btn.pack(side="left", padx=6)

#         self.send_btn = self._button(
#             btn_frame,
#             "💬 Send",
#             lambda: threading.Thread(
#                 target=self.process_text_input,
#                 daemon=True
#             ).start()
#         )
#         self.send_btn.pack(side="left", padx=6)

#         # ---------- CHAT INPUT ----------
#         self._section(container, "Chat Input")
#         self.chat_entry = tk.Entry(
#             container,
#             font=("Segoe UI", 12),
#             bg=ENTRY_BG,
#             fg=TEXT_COLOR,
#             insertbackground=TEXT_COLOR,
#             relief="flat"
#         )
#         self.chat_entry.pack(fill="x", padx=4, pady=(0, 6))

#     # ---------------- UI HELPERS ----------------
#     def _section(self, parent, title):
#         tk.Label(
#             parent,
#             text=title,
#             font=("Segoe UI", 11, "bold"),
#             bg=BG_COLOR,
#             fg=SUBTEXT_COLOR
#         ).pack(anchor="w", pady=(8, 2))

#     def _text(self, parent, height, fg=TEXT_COLOR):
#         box = tk.Text(
#             parent,
#             height=height,
#             wrap="word",
#             bg=CARD_COLOR,
#             fg=fg,
#             insertbackground=fg,
#             relief="flat"
#         )
#         box.pack(fill="x", padx=4)
#         return box

#     def _button(self, parent, text, command):
#         btn = tk.Button(
#             parent,
#             text=text,
#             font=("Segoe UI", 12, "bold"),
#             bg=BTN_COLOR,
#             fg="white",
#             activebackground=BTN_HOVER,
#             activeforeground="white",
#             relief="flat",
#             padx=18,
#             pady=6,
#             command=command
#         )
#         btn.bind("<Enter>", lambda e: btn.config(bg=BTN_HOVER))
#         btn.bind("<Leave>", lambda e: btn.config(bg=BTN_COLOR))
#         return btn

#     # ---------------- VOICE PIPELINE ----------------
#     def pipeline(self):
#         with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
#             audio_file = tmp.name

#         try:
#             self.logger.log("🎙️ Recording...", self.log_box)
#             record_audio(audio_file)

#             transcript = transcribe_audio(audio_file).strip()
#             print(f" Whisper returned text: {transcript}")

#             self.logger.log(" " + transcript, self.transcript_box)
#             self.handle_intent_and_execute(transcript)

#         except Exception as e:
#             self.logger.log(f"❌ Pipeline error: {e}", self.log_box)

#         finally:
#             self.cleanup_files(audio_file)

#     # ---------------- CHAT INPUT ----------------
#     def process_text_input(self):
#         transcript = self.chat_entry.get().strip()
#         if not transcript:
#             return

#         self.chat_entry.delete(0, tk.END)
#         self.logger.log(" " + transcript, self.transcript_box)
#         self.handle_intent_and_execute(transcript)

#     # ---------------- INTENT HANDLER ----------------
#     def handle_intent_and_execute(self, transcript: str):
#         response = extract_intent(transcript)

#         if isinstance(response, str):
#             try:
#                 response = json.loads(response)
#             except:
#                 response = {"intent": "other", "slots": {}}

#         intent = response.get("intent")
#         slots = response.get("slots", {}) or {}

#         self.logger.log(" " + json.dumps(response, indent=2), self.intent_box)

#         if intent == "change_volume":
#             result = (
#                 vcc.set_volume_percent(slots)
#                 if any(k in slots for k in ("percent", "value", "level", "amount"))
#                 else vc(slots)
#             )
#             self.logger.log(result, self.action_box)

#         elif intent == "get_weather":
#             self.logger.log(weather.get_weather(slots), self.action_box)

#         elif intent == "send_email":
#             from executor import gmail_sender
#             self.logger.log(gmail_sender.send_email(slots), self.action_box)

#         elif intent in ("change_brightness", "set_brightness"):
#             self.logger.log(bc.change_brightness(slots), self.action_box)

#         elif intent == "power_action":
#             from executor import power_control as pc
#             from utils.confirm import confirm_voice
#             from utils.tts import speak

#             action = slots.get("action", "lock")
#             confirmed = confirm_voice(
#                 f"Do you want to {action} the system? Say yes to confirm.",
#                 retries=1,
#                 record_seconds=4
#             )

#             if confirmed:
#                 speak("Confirmed. Executing now.", block=False)
#                 self.logger.log(pc.handle_power_action(slots), self.action_box)
#             else:
#                 speak("Cancelled.", block=False)
#                 self.logger.log(" Action cancelled.", self.action_box)

#         elif intent == "create_event":
#             self.logger.log(cal.create_event(slots), self.action_box)

#         else:
#             self.logger.log(f" Action not implemented: {intent}", self.action_box)

#     # ---------------- CLEANUP ----------------
#     def cleanup_files(self, audio_file):
#         try:
#             if os.path.exists(audio_file):
#                 os.remove(audio_file)
#             txt = audio_file + ".txt"
#             if os.path.exists(txt):
#                 os.remove(txt)
#         except Exception as e:
#             self.logger.log(f"Cleanup failed: {e}", self.log_box)

#     def run(self):
#         self.root.mainloop()


