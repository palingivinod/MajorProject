import subprocess
import os


OPEN_COMMANDS = {
    "calculator": "calc",
    "notepad": "notepad",
    "cmd": "cmd",
    "camera": "start microsoft.windows.camera:",
    "explorer": "explorer",
    "file explorer": "explorer",
    "settings": "start ms-settings:",
    "control panel": "control",
    "task manager": "taskmgr",
    "paint": "mspaint",
    "word": "start winword",
    "excel": "start excel",
    "powerpoint": "start powerpnt"
}



PROCESS_NAMES = {
    "calculator": "CalculatorApp.exe",
    "notepad": "notepad.exe",
    "cmd": "cmd.exe",
    "camera": "WindowsCamera.exe",
    "explorer": "explorer.exe",
    "settings": "SystemSettings.exe",
    "control panel": "control.exe",
    "task manager": "Taskmgr.exe",
    "paint": "mspaint.exe",
    "word": "WINWORD.EXE",
    "excel": "EXCEL.EXE",
    "powerpoint": "POWERPNT.EXE"
}



def open_app(slots):
    app = slots.get("app", "").lower()

    if not app:
        return "Application name missing."

    if app in OPEN_COMMANDS:
        try:
            command = OPEN_COMMANDS[app]

            if command.startswith("start"):
                os.system(command)
            else:
                subprocess.Popen(command)

            return f"Opened {app}."

        except Exception as e:
            return f"Failed to open {app}: {e}"

    return "Application not supported."



def close_app(slots):
    app = slots.get("app", "").lower()

    if not app:
        return "Application name missing."

    if app in PROCESS_NAMES:
        try:
            subprocess.run(
                ["taskkill", "/f", "/im", PROCESS_NAMES[app]],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return f"Closed {app}."
        except:
            return f"Could not close {app}."

    return "Application not supported."
