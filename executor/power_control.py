# executor/power_control.py
import os
import subprocess
import ctypes
from ctypes import wintypes

# Windows API handles
try:
    user32 = ctypes.WinDLL('user32', use_last_error=True)
except Exception:
    user32 = None

def lock_screen():
    """
    Locks the workstation (Windows+L).
    """
    try:
        if user32:
            result = user32.LockWorkStation()
            if result == 0:
                return "⚠️ Failed to lock workstation."
            return "🔒 Screen locked."
        else:
            return "⚠️ Lock not available on this system."
    except Exception as e:
        return f"⚠️ Lock failed: {e}"

def _call_set_suspend_state(hibernate: bool = False, force: bool = False, disable_wake_event: bool = True):
    """
    Use SetSuspendState via PowrProf. Returns True on success (best-effort).
    """
    try:
        powrprof = ctypes.WinDLL('PowrProf')
        SetSuspendState = powrprof.SetSuspendState
        SetSuspendState.argtypes = (wintypes.BOOL, wintypes.BOOL, wintypes.BOOL)
        SetSuspendState.restype = wintypes.BOOL
        res = SetSuspendState(hibernate, force, disable_wake_event)
        return bool(res)
    except Exception:
        return False

def sleep_system():
    """
    Puts the system to sleep (S3). Best-effort; may require privileges.
    """
    try:
        ok = _call_set_suspend_state(hibernate=False, force=False, disable_wake_event=True)
        if ok:
            return "💤 System going to sleep."
    except Exception:
        pass

    # Fallback: rundll32
    try:
        cmd = ['rundll32.exe', 'powrprof.dll,SetSuspendState', '0,1,0']
        subprocess.run(cmd, check=True)
        return "💤 System going to sleep (fallback)."
    except Exception as e:
        return f"⚠️ Sleep failed: {e}"

def hibernate_system():
    """
    Attempts to hibernate the system (S4). Hibernate must be enabled.
    """
    try:
        ok = _call_set_suspend_state(hibernate=True, force=False, disable_wake_event=True)
        if ok:
            return "🛌 System hibernating."
    except Exception:
        pass

    # Fallback: rundll32 with Hibernate (may not work on all Windows)
    try:
        cmd = ['rundll32.exe', 'powrprof.dll,SetSuspendState', 'Hibernate']
        subprocess.run(cmd, check=True)
        return "🛌 System hibernating (fallback)."
    except Exception as e:
        return f"⚠️ Hibernate failed: {e}"

def handle_power_action(slots: dict):
    """
    slots expected:
      {"action": "lock"/"sleep"/"hibernate"}
    """
    action = (slots.get("action") or "").lower()

    if action == "lock":
        return lock_screen()
    elif action == "sleep":
        return sleep_system()
    elif action == "hibernate":
        return hibernate_system()
    else:
        return "❌ Unknown power action. Supported: lock, sleep, hibernate."
