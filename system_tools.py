import psutil
import shutil

def get_system_report():
    # CPU & RAM
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    
    # Battery Status
    battery = psutil.sensors_battery()
    if battery:
        percent = battery.percent
        plugged = "plugged in" if battery.power_plugged else "on battery power"
        batt_str = f"Battery is at {percent} percent and {plugged}."
    else:
        batt_str = "No battery sensor detected."
        
    # Disk Storage (C: Drive)
    total, used, free = shutil.disk_usage("C:\\")
    free_gb = free // (2**30)
    
    return f"CPU usage is currently at {cpu} percent, memory load is at {ram} percent, and {batt_str} You have {free_gb} gigabytes free on your main drive, sir."

def get_battery():
    battery = psutil.sensors_battery()
    if battery:
        plugged = "charging" if battery.power_plugged else "discharging"
        return f"Battery is at {battery.percent} percent and {plugged}, sir."
    return "Battery details are unavailable on this machine, sir."  