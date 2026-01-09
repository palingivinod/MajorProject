import time
import tkinter as tk
import threading
import os
import tempfile
import json
from tkinter import ttk, scrolledtext, font
from utils.tts import speak
from utils import Logger
from audio.recorder import record_audio
from audio.transcriber import transcribe_audio
from nlu.intent_extrator import extract_intent
from executor import calendar_api as cal
from executor import weather
from executor import brightness_control as bc
from executor import volume_control as vcc
from executor.volume_control import change_volume as vc
from executor import music_control as mc
from executor import code_agent as ca
from executor import system_monitoring as sm

class VoiceAssistantApp:
    def __init__(self):
        self.muted = False 
        self.listening = False
        self.speaking = False

        # Tkinter setup - Dark theme with borders
        self.root = tk.Tk()
        self.root.title("Assistant AI")
        self.root.geometry("1100x750")
        
        # Color scheme
        self.bg_color = "#1a1a2e"
        self.card_color = "#16213e"
        self.accent_color = "#0f3460"
        self.border_color = "#4cc9f0"
        self.text_color = "#e6e6e6"
        self.user_color = "#4cc9f0"
        self.ai_color = "#f72585"
        self.input_bg = "#0d1b2a"
        self.panel_bg = "#0d1b2a"
        
        self.root.configure(bg=self.bg_color)

        self.logger = Logger()
        self.create_ui()

    def create_ui(self):
        # Main container
        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # ===== LEFT PANEL (Hidden) =====
        self.create_left_panel(main_container)
        
        # ===== MAIN AREA =====
        main_area = tk.Frame(main_container, bg=self.card_color, 
                            relief="solid", borderwidth=2,
                            highlightbackground=self.border_color,
                            highlightthickness=2)
        main_area.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Header with gradient effect
        header = tk.Frame(main_area, bg=self.accent_color, height=70)
        header.pack(fill="x")
        header.pack_propagate(False)
        
        # Title with cool emoji
        title_frame = tk.Frame(header, bg=self.accent_color)
        title_frame.pack(side="left", padx=25, pady=15)
        
        tk.Label(title_frame, 
                text="🤖",  # Robot emoji
                font=('Segoe UI Emoji', 22),
                bg=self.accent_color,
                fg=self.border_color).pack(side="left")
        
        tk.Label(title_frame, 
                text="Assistant AI",
                font=('Segoe UI', 22, 'bold'),
                bg=self.accent_color,
                fg="#ffffff").pack(side="left", padx=10)
        
        # Right side buttons
        btn_frame = tk.Frame(header, bg=self.accent_color)
        btn_frame.pack(side="right", padx=25, pady=15)
        
        # Mute button with better emoji
        self.mute_btn = tk.Button(btn_frame,
                                 text="🔊",  # Speaker emoji
                                 font=('Segoe UI Emoji', 16),
                                 bg="#2d3748",
                                 fg="#ffffff",
                                 relief="raised",
                                 borderwidth=2,
                                 width=3,
                                 command=self.toggle_mute)
        self.mute_btn.pack(side="right", padx=8)
        
        # Panel toggle button
        self.panel_toggle = tk.Button(btn_frame,
                                     text="📊",  # Chart emoji
                                     font=('Segoe UI Emoji', 16),
                                     bg="#2d3748",
                                     fg="#ffffff",
                                     relief="raised",
                                     borderwidth=2,
                                     width=3,
                                     command=self.toggle_left_panel)
        self.panel_toggle.pack(side="right", padx=8)
        
        # Status indicator
        self.status_label = tk.Label(btn_frame,
                                    text="● Ready",
                                    font=('Segoe UI', 11, 'bold'),
                                    bg=self.accent_color,
                                    fg="#90ee90")
        self.status_label.pack(side="right", padx=15)
        
        # Chat display area
        chat_container = tk.Frame(main_area, bg=self.card_color)
        chat_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_container,
            wrap=tk.WORD,
            font=('Segoe UI', 13),
            bg=self.card_color,
            fg=self.text_color,
            relief="flat",
            borderwidth=0,
            state='disabled',
            padx=20,
            pady=20
        )
        self.chat_display.pack(fill="both", expand=True)
        
        # Configure message styles
        self.chat_display.tag_config("user", 
                                   foreground=self.user_color,
                                   font=('Segoe UI', 13, 'bold'),
                                   lmargin1=15,
                                   lmargin2=15,
                                   spacing1=8)
        
        self.chat_display.tag_config("assistant",
                                   foreground=self.ai_color,
                                   font=('Segoe UI', 13),
                                   lmargin1=15,
                                   lmargin2=15,
                                   spacing1=8,
                                   spacing3=5)
        
        # Welcome message
        welcome_msg = """🎉 Welcome to Assistant AI! 🎉

✨ What I can do for you:
• 🔊 Control volume & brightness
• 🌤️ Check weather & system status  
• 🎵 Play/pause music
• 📅 Manage calendar & emails
• 💻 Open VS Code & run programs
• ⚡ Power actions (lock/restart)

💬 How to use:
1. Type your command below
2. OR click the 🎤 button to speak
3. View details in 📊 panel

Ready when you are! 👇"""
        
        self.add_chat_message("assistant", welcome_msg)
        
        # ===== INPUT AREA (Bottom) - SIMPLIFIED AND FIXED =====
        input_frame = tk.Frame(main_area, bg=self.card_color)
        input_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Simple container
        input_container = tk.Frame(input_frame, bg=self.input_bg)
        input_container.pack(fill="x", padx=0, pady=0)
        
        # SIMPLE Text input - Entry widget instead of Text widget
        self.chat_entry = tk.Entry(
            input_container,
            font=('Segoe UI', 13),
            bg=self.input_bg,
            fg=self.text_color,
            relief="flat",
            borderwidth=0,
            insertbackground=self.border_color
        )
        self.chat_entry.pack(side="left", fill="x", expand=True, padx=15, pady=15)
        self.chat_entry.bind("<Return>", lambda e: self.process_text_input())
        
        # Set placeholder text
        self.chat_entry.insert(0, "💭 Type your command here...")
        self.chat_entry.config(fg="#718096")
        
        # Bind events for placeholder (for Entry widget)
        self.chat_entry.bind("<FocusIn>", self.on_focus_in)
        self.chat_entry.bind("<FocusOut>", self.on_focus_out)
        
        # Right side buttons
        btn_frame = tk.Frame(input_container, bg=self.input_bg)
        btn_frame.pack(side="right", padx=(0, 10), pady=10)
        
        # Send button
        send_btn = tk.Button(btn_frame,
                            text="🚀",
                            font=('Segoe UI Emoji', 16),
                            bg="#805ad5",
                            fg="white",
                            relief="raised",
                            borderwidth=2,
                            width=3,
                            height=1,
                            command=self.process_text_input)
        send_btn.pack(side="right", padx=5)
        
        # Microphone button
        self.mic_btn = tk.Button(btn_frame,
                                text="🎤",
                                font=('Segoe UI Emoji', 20),
                                bg="#38a169",
                                fg="white",
                                relief="raised",
                                borderwidth=2,
                                width=4,
                                height=1,
                                command=self.toggle_listening)
        self.mic_btn.pack(side="right", padx=5)

    def create_left_panel(self, parent):
        # Left panel (hidden by default)
        self.left_panel = tk.Frame(parent, 
                                  bg=self.panel_bg, 
                                  width=320,
                                  relief="solid", 
                                  borderwidth=2,
                                  highlightbackground=self.border_color,
                                  highlightthickness=2)
        
        # Panel header
        panel_header = tk.Frame(self.left_panel, bg=self.accent_color, height=60)
        panel_header.pack(fill="x")
        panel_header.pack_propagate(False)
        
        tk.Label(panel_header, 
                text="🔍 Details Panel",
                font=('Segoe UI', 16, 'bold'),
                bg=self.accent_color,
                fg="white").pack(side="left", padx=20, pady=15)
        
        # Close button
        close_btn = tk.Button(panel_header,
                             text="✕",
                             font=('Segoe UI', 14),
                             bg="#2d3748",
                             fg="white",
                             relief="flat",
                             command=self.toggle_left_panel)
        close_btn.pack(side="right", padx=20)
        
        # Panel content
        panel_content = tk.Frame(self.left_panel, bg=self.panel_bg)
        panel_content.pack(fill="both", expand=True, padx=15, pady=15)
        
        # ===== DROPDOWN SECTIONS =====
        
        # 1. Transcript dropdown
        self.create_panel_dropdown(
            panel_content,
            "📝 Transcript",
            "transcript",
            "#4cc9f0"  # Cyan
        )
        
        # 2. Intent dropdown  
        self.create_panel_dropdown(
            panel_content,
            "🎯 Intent",
            "intent", 
            "#f72585"  # Pink
        )
        
        # 3. Logs dropdown
        self.create_panel_dropdown(
            panel_content,
            "📋 System Logs",
            "logs",
            "#f9c74f"  # Yellow
        )
        
        # Info text at bottom
        info_frame = tk.Frame(panel_content, bg=self.panel_bg)
        info_frame.pack(side="bottom", fill="x", pady=20)
        
        tk.Label(info_frame,
                text="💡 Click arrows to expand/collapse",
                font=('Segoe UI', 10),
                bg=self.panel_bg,
                fg="#a0aec0").pack()

    def create_panel_dropdown(self, parent, title, section_id, color):
        # Dropdown container with border
        dropdown_frame = tk.Frame(parent, 
                                 bg=self.panel_bg,
                                 relief="solid", 
                                 borderwidth=1,
                                 highlightbackground="#4a5568",
                                 highlightthickness=1)
        dropdown_frame.pack(fill="x", pady=8)
        
        # Dropdown button
        btn = tk.Button(dropdown_frame,
                       text=f"▼ {title}",
                       font=('Segoe UI', 12, 'bold'),
                       bg="#2d3748",
                       fg=color,
                       relief="flat",
                       anchor="w",
                       padx=15,
                       command=lambda sid=section_id, t=title, c=color: self.toggle_panel_section(sid, t, c))
        btn.pack(fill="x", padx=0, pady=0)
        
        # Content frame (hidden by default)
        content_frame = tk.Frame(dropdown_frame, bg="#2d3748")
        
        # Create text widget
        text_widget = scrolledtext.ScrolledText(
            content_frame,
            height=5,
            wrap="word",
            font=('Consolas', 10),
            bg="#1a202c",
            fg=color,
            relief="flat",
            borderwidth=0,
            padx=10,
            pady=10
        )
        text_widget.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Store references
        if section_id == "transcript":
            self.transcript_btn = btn
            self.transcript_frame = content_frame
            self.transcript_box = text_widget
        elif section_id == "intent":
            self.intent_btn = btn
            self.intent_frame = content_frame
            self.intent_box = text_widget
        elif section_id == "logs":
            self.logs_btn = btn
            self.logs_frame = content_frame
            self.log_box = text_widget

    # ===== SIMPLE PLACEHOLDER METHODS FOR ENTRY WIDGET =====
    
    def on_focus_in(self, event):
        """Handle focus in event for Entry widget"""
        if self.chat_entry.get() == "💭 Type your command here...":
            self.chat_entry.delete(0, tk.END)
            self.chat_entry.config(fg=self.text_color)
    
    def on_focus_out(self, event):
        """Handle focus out event for Entry widget"""
        if not self.chat_entry.get().strip():
            self.chat_entry.delete(0, tk.END)
            self.chat_entry.insert(0, "💭 Type your command here...")
            self.chat_entry.config(fg="#718096")

    def toggle_left_panel(self):
        if self.left_panel.winfo_ismapped():
            self.left_panel.pack_forget()
            self.panel_toggle.config(text="📊")
        else:
            self.left_panel.pack(side="left", fill="y")
            self.panel_toggle.config(text="←")

    def toggle_panel_section(self, section_id, title, color):
        if section_id == "transcript":
            btn = self.transcript_btn
            frame = self.transcript_frame
        elif section_id == "intent":
            btn = self.intent_btn
            frame = self.intent_frame
        else:  # logs
            btn = self.logs_btn
            frame = self.logs_frame
        
        if frame.winfo_ismapped():
            frame.pack_forget()
            btn.config(text=f"▼ {title}", fg=color)
        else:
            frame.pack(fill="x", pady=(5, 0))
            btn.config(text=f"▲ {title}", fg=color)

    def add_chat_message(self, sender, message):
        self.chat_display.config(state='normal')
        
        # Add timestamp
        timestamp = time.strftime("%H:%M")
        
        if sender == "assistant":
            self.chat_display.insert(tk.END, f"[{timestamp}] 🤖 Assistant:\n", "assistant")
            self.chat_display.insert(tk.END, message + "\n\n")
        else:
            self.chat_display.insert(tk.END, f"[{timestamp}] 👤 You:\n", "user")
            self.chat_display.insert(tk.END, message + "\n\n")
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state='disabled')

    def toggle_mute(self):
        self.muted = not self.muted
        if self.muted:
            self.mute_btn.config(text="🔈", bg="#e53e3e", fg="white")
            self.status_label.config(text="● Muted", fg="#fc8181")
        else:
            self.mute_btn.config(text="🔊", bg="#2d3748", fg="white")
            self.status_label.config(text="● Ready", fg="#90ee90")

    def toggle_listening(self):
        if not self.listening:
            self.listening = True
            self.mic_btn.config(text="⏹️", bg="#e53e3e", fg="white")  # Stop emoji
            self.status_label.config(text="● Listening...", fg="#4cc9f0")
            self.add_chat_message("assistant", "🎤 Listening... Speak now!")
            threading.Thread(target=self.continuous_listen, daemon=True).start()
        else:
            self.listening = False
            self.mic_btn.config(text="🎤", bg="#38a169", fg="white")
            self.status_label.config(text="● Ready", fg="#90ee90")

    def continuous_listen(self):
        while self.listening:
            while self.speaking:
                time.sleep(0.1)

            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                audio_file = tmp.name

            try:
                self.logger.log("🎧 Listening started...", self.log_box)
                record_audio(audio_file)
                transcript = transcribe_audio(audio_file).strip()
                print(f"Transcript: {transcript}")

                if transcript:
                    self.add_chat_message("user", f"🗣️ {transcript}")
                    self.logger.log(f"🎤 Transcript: {transcript}", self.transcript_box)
                    self.handle_intent_and_execute(transcript)

            except Exception as e:
                self.logger.log(f"❌ Error: {e}", self.log_box)
                self.add_chat_message("assistant", f"⚠️ Error: {str(e)}")

            finally:
                self.cleanup_files(audio_file)

    def process_text_input(self):
        # Get text from Entry widget
        transcript = self.chat_entry.get().strip()
        
        # Check if it's placeholder or empty
        if not transcript or transcript == "💭 Type your command here...":
            return
        
        # Clear the input
        self.chat_entry.delete(0, tk.END)
        
        # Add message to chat
        self.add_chat_message("user", f"⌨️ {transcript}")
        self.logger.log(f"⌨️ Text input: {transcript}", self.transcript_box)
        
        # Process in background thread
        threading.Thread(target=self.handle_intent_and_execute, args=(transcript,), daemon=True).start()

    def handle_intent_and_execute(self, transcript: str):
        response = extract_intent(transcript)

        if isinstance(response, str):
            try:
                response = json.loads(response)
            except:
                response = {"intent": "other", "slots": {}}

        intent = response.get("intent")
        slots = response.get("slots", {}) or {}

        self.logger.log(f"🎯 Intent detected: {response}", self.intent_box)

        # Process intents
        result = ""
        action_icon = "⚡"
        
        if intent == "change_volume":
            if any(k in slots for k in ("percent", "value", "level", "amount")):
                result = vcc.set_volume_percent(slots)
            else:
                result = vc(slots)
            action_icon = "🔊"
            self.logger.log(f"{action_icon} Action: {result}", self.log_box)
            if not self.muted:
                self.speak_and_wait(result)

        elif intent == "get_weather":
            result = weather.get_weather(slots)
            action_icon = "🌤️"
            self.logger.log(f"{action_icon} Action: {result}", self.log_box)
            if not self.muted:
                self.speak_and_wait(result)

        elif intent == "send_email":
            from executor import gmail_sender
            result = gmail_sender.send_email(slots)
            action_icon = "📧"
            self.logger.log(f"{action_icon} Action: {result}", self.log_box)
            if not self.muted:
                self.speak_and_wait(result)

        elif intent in ("change_brightness", "set_brightness"):
            result = bc.change_brightness(slots)
            action_icon = "💡"
            self.logger.log(f"{action_icon} Action: {result}", self.log_box)
            if not self.muted:
                self.speak_and_wait(result)

        elif intent == "power_action":
            from executor import power_control as pc
            from utils.confirm import confirm_voice
            action = slots.get("action", "lock")
            prompt = f"Do you want to {action} the system? Say yes to confirm."
            confirmed = confirm_voice(prompt, retries=1, record_seconds=4)
            if confirmed:
                speak("Confirmed. Executing now.", block=False)
                result = pc.handle_power_action(slots)
                action_icon = "⚡"
                self.logger.log(f"{action_icon} Action: {result}", self.log_box)
                if not self.muted:
                    self.speak_and_wait(result)
            else:
                speak("Cancelled.", block=False)
                result = "Action cancelled."
                action_icon = "❌"
                self.logger.log(f"{action_icon} Action cancelled", self.log_box)

        elif response.get("intent") == "create_event":
            result = cal.create_event(response.get("slots", {}))
            action_icon = "📅"
            self.logger.log(f"{action_icon} Action: {result}", self.log_box)
            if not self.muted:
                self.speak_and_wait(result)

        elif intent == "music_control":
            action = slots.get("action")
            if action == "play_pause":
                result = mc.play_pause()
                action_icon = "⏯️"
            elif action == "next":
                result = mc.next_track()
                action_icon = "⏭️"
            elif action == "previous":
                result = mc.previous_track()
                action_icon = "⏮️"
            else:
                result = "Unknown music action."
                action_icon = "🎵"
            self.logger.log(f"{action_icon} Action: {result}", self.log_box)
            if not self.muted:
                self.speak_and_wait(result)

        elif intent == "code_action":
            action = slots.get("action")
            if action == "open_vscode":
                result = ca.open_vscode()
                action_icon = "💻"
            elif action == "close_vscode":
                result = ca.close_vscode()
                action_icon = "❌"
            elif action == "create_file":
                result = ca.create_file(slots)
                action_icon = "📄"
            elif action == "write_code":
                result = ca.write_code(slots)
                action_icon = "✍️"
            elif action == "run_code":
                result = ca.run_code(slots)
                action_icon = "🚀"
            else:
                result = "Unknown code action."
                action_icon = "💻"
            self.logger.log(f"{action_icon} Action: {result}", self.log_box)
            if not self.muted:
                self.speak_and_wait(result)

        elif intent == "system_monitor":
            action = slots.get("action", "summary")
            if action == "cpu":
                result = sm.get_cpu_usage()
                action_icon = "🖥️"
            elif action == "memory":
                result = sm.get_memory_usage()
                action_icon = "🧠"
            elif action == "disk":
                result = sm.get_disk_usage()
                action_icon = "💾"
            elif action == "battery":
                result = sm.get_battery_status()
                action_icon = "🔋"
            else:
                result = sm.get_system_summary()
                action_icon = "📊"
            self.logger.log(f"{action_icon} Action: {result}", self.log_box)
            if not self.muted:
                self.speak_and_wait(result)

        else:
            result = "🤔 I didn't understand that command. Try: 🔊 volume, 🌤️ weather, 🎵 music, or 💻 system commands."
            action_icon = "❓"
            self.logger.log(f"{action_icon} Unknown intent: {intent}", self.log_box)
            if not self.muted:
                self.speak_and_wait(result)
        
        # Show result in chat with emoji
        self.add_chat_message("assistant", f"{action_icon} {result}")
        
        # Stop listening
        if self.listening:
            self.listening = False
            self.mic_btn.config(text="🎤", bg="#38a169", fg="white")
            self.status_label.config(text="● Ready", fg="#90ee90")

    def speak_and_wait(self, text):
        self.speaking = True
        speak(text, block=True) 
        self.speaking = False

    def cleanup_files(self, audio_file):
        try:
            if os.path.exists(audio_file):
                os.remove(audio_file)
            txt_file = audio_file + ".txt"
            if os.path.exists(txt_file):
                os.remove(txt_file)
            self.logger.log("🧹 Cleaned up temporary files", self.log_box)
        except Exception as e:
            self.logger.log(f"⚠️ Cleanup failed: {e}", self.log_box)

    def run(self):
        # Center window
        self.root.update_idletasks()
        width = 1100
        height = 750
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
        
        self.root.mainloop()

# To run the app
if __name__ == "__main__":
    app = VoiceAssistantApp()
    app.run()


