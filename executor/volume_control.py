from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Initialize volume interface once
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))

def change_volume(slots):
    """
    slots: dict with "action" key ("increase" or "decrease")
    """
    current = volume.GetMasterVolumeLevelScalar()
    action = slots.get("action")

    if action == "increase":
        new_level = min(current + 0.2, 1.0)
    elif action == "decrease":
        new_level = max(current - 0.2, 0.0)
    else:
        new_level = current

    volume.SetMasterVolumeLevelScalar(new_level, None)
    return f"🔊 Volume set to {int(new_level*100)}%"
