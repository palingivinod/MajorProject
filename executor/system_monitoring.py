import psutil
import platform

def get_cpu_usage():
    cpu = psutil.cpu_percent(interval=1)
    return f"🧠 CPU Usage: {cpu}%"

def get_memory_usage():
    mem = psutil.virtual_memory()
    used = round(mem.used / (1024 ** 3), 2)
    total = round(mem.total / (1024 ** 3), 2)
    return f"💾 RAM Usage: {used} GB / {total} GB ({mem.percent}%)"

def get_disk_usage():
    disk = psutil.disk_usage("/")
    used = round(disk.used / (1024 ** 3), 2)
    total = round(disk.total / (1024 ** 3), 2)
    return f"💽 Disk Usage: {used} GB / {total} GB ({disk.percent}%)"

def get_battery_status():
    battery = psutil.sensors_battery()
    if battery is None:
        return "🔋 Battery information not available."

    status = "Charging" if battery.power_plugged else "Not Charging"
    return f"🔋 Battery: {battery.percent}% ({status})"

def get_system_summary():
    return (
        f"🖥️ System: {platform.system()} {platform.release()}\n"
        f"{get_cpu_usage()}\n"
        f"{get_memory_usage()}\n"
        f"{get_disk_usage()}\n"
        f"{get_battery_status()}"
    )
