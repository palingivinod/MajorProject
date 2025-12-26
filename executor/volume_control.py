from pycaw.pycaw import AudioUtilities

volume = AudioUtilities.GetSpeakers().EndpointVolume

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
    elif action == "full":
        new_level = 1.0
    elif action == "mute":
        new_level = 0.0
    else:
        new_level = current

    volume.SetMasterVolumeLevelScalar(new_level, None)
    return f"Volume set to {int(new_level*100)}%"

def set_volume_percent(slots):
    """
    Set volume to a specific percent.
    Accepts slots like:
      {"percent": 30}
      {"percent": "30%"}
      {"value": 30}
      {"level": "45%"}
      {"level": "0%"}
    Returns user-friendly message (same style as change_volume).
    """
    p = slots.get("percent") or slots.get("value") or slots.get("level") or slots.get("amount")
    if p is None:
        return "No percent provided. Use slots like {'percent':30}."

    try:
        if isinstance(p, str):
            p_s = p.strip()
            if p_s.endswith("%"):
                p_val = float(p_s.rstrip("%"))
            else:
                p_val = float(p_s)
        else:
            p_val = float(p)
    except Exception:
        return "Invalid percent value. Provide a number between 0 and 100 (e.g., 30 or '30%')."

    p_val = max(0.0, min(100.0, p_val))
    scalar = p_val / 100.0

    try:
        volume.SetMasterVolumeLevelScalar(scalar, None)
        return f"Volume set to {int(p_val)}%"
    except Exception as e:
        return f"Failed to set volume: {e}"
