import screen_brightness_control as sbc

def get_brightness():
    """
    Returns current brightness (0–100) or None.
    """
    try:
        values = sbc.get_brightness()
        if isinstance(values, list) and values:
            return int(values[0])
        return int(values)
    except Exception:
        return None


def set_brightness(level: int):
    """
    Set brightness to `level` (0–100).
    """
    try:
        level = max(0, min(100, int(level)))
        sbc.set_brightness(level)
        return f" Brightness set to {level}%"
    except Exception as e:
        return f"❌ Failed to set brightness: {e}"


def change_brightness(slots: dict):
    """
    slots expected:
      {
        "action": "increase" / "decrease" / "set",
        "step": optional int,
        "value": optional int
      }
    """

    action = (slots.get("action") or "").lower()
    step = slots.get("step", 10)
    value = slots.get("value")

    try:
        step = abs(int(step))
    except:
        step = 10

    current = get_brightness()
    if current is None:
        current = 50  # safe fallback

    # INCREASE
    if action in ("increase", "up", "raise"):
        new = min(100, current + step)
        return set_brightness(new)

    # DECREASE
    elif action in ("decrease", "down", "lower"):
        new = max(0, current - step)
        return set_brightness(new)

    # SET ABSOLUTE
    elif action == "set":
        if value is None:
            return " No brightness value provided."
        try:
            new = max(0, min(100, int(value)))
            return set_brightness(new)
        except:
            return " Invalid brightness value."

    return f" Unknown brightness action: {action}"

