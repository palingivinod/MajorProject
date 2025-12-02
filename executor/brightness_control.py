import math
import ctypes
import os

try:
    import wmi
    _HAS_WMI = True
except Exception:
    _HAS_WMI = False

def _get_wmi_monitor():
    try:
        c = wmi.WMI(namespace='wmi')
        methods = c.WmiMonitorBrightnessMethods()
        status = c.WmiMonitorBrightness()
        return methods, status
    except Exception:
        return None, None

def get_brightness():
    """
    Returns current brightness as int (0-100) or None if unavailable.
    """
    if _HAS_WMI:
        methods, status = _get_wmi_monitor()
        if status and len(status) > 0:
            return int(status[0].CurrentBrightness)
 
    try:
        # Use Windows API via ctypes (may not give brightness)
        return None
    except Exception:
        return None

def set_brightness(level: int):
    """
    Set brightness to `level` (0-100). Returns success message or error string.
    """
    level = max(0, min(100, int(level)))
    if _HAS_WMI:
        try:
            methods, status = _get_wmi_monitor()
            if methods and len(methods) > 0:
                # Timeout 0 = immediate
                methods[0].WmiSetBrightness(0, level)
                return f" Brightness set to {level}%"
        except Exception as e:
            return f" Failed to set brightness via WMI: {e}"

    # Fallback: try powershell (requires Windows)
    try:
        # Use powershell command to set brightness (works on many systems)
        ps_cmd = f'(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(0,{level})'
        cmd = ["powershell", "-Command", ps_cmd]
        # use os.system to keep it simple; could use subprocess.run
        res = os.system(" ".join(cmd))
        if res == 0:
            return f" Brightness set to {level}% (via PowerShell)"
        else:
            return f" Could not set brightness with PowerShell (exit {res})"
    except Exception as e:
        return f" Failed to set brightness: {e}"

def change_brightness(slots: dict):
    """
    slots expected:
      {"action":"increase"/"decrease"/"set", "value": optional int}
    """
    action = slots.get("action", "").lower()
    value = slots.get("value", None)

    current = get_brightness()
    
    # If we cannot read current brightness, assume 50 for relative ops
    if current is None:
        current = 50

    if action == "increase":
        step = int(slots.get("step", 10))
        new = min(100, current + step)
        return set_brightness(new)
    elif action == "decrease":
        step = int(slots.get("step", 10))
        new = max(0, current - step)
        return set_brightness(new)
    elif action == "set":
        if value is None:
            return " No brightness value provided."
        try:
            new = int(value)
            return set_brightness(new)
        except ValueError:
            return " Invalid brightness value."
    else:
        return " Unknown brightness action."
