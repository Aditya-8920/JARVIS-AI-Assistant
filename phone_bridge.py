import os
import subprocess
import time
import urllib.parse
import re
import pywhatkit

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ADB_PATH = os.path.join(SCRIPT_DIR, "platform-tools", "adb.exe")

if not os.path.exists(ADB_PATH):
    ADB_PATH = "adb"

# ==========================================
# CONTACTS LIST 
# ==========================================
# Default Dummy numbers (GitHub ke liye)
CONTACTS = {
    "mummy": "9999999999",
    "mom": "9999999999",
    "didi": "8888888888",
    "sister": "8888888888",
    "papa": "7777777777",
    "dad": "7777777777"
}

# Agar local PC par private file exist karegi toh real numbers load honge
try:
    from my_contacts import PRIVATE_CONTACTS
    CONTACTS.update(PRIVATE_CONTACTS)
except ImportError:
    pass

def run_adb(command):
    try:
        cmd = f'"{ADB_PATH}" {command}'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {e}"

def check_phone_connection():
    out = run_adb("devices")
    lines = [l for l in out.splitlines() if "\tdevice" in l]
    if lines:
        return True, lines[0].split("\t")[0]
    return False, "No phone detected via ADB."

def wake_screen():
    run_adb("shell input keyevent 224")
    run_adb("shell wm dismiss-keyguard")

def make_call(target, sim_slot=1):
    target_str = str(target).lower().strip()
    phone_number = None
    
    # Check contact dictionary
    for name, num in CONTACTS.items():
        if name in target_str or target_str in name:
            phone_number = num
            break
            
    # Check direct number
    if not phone_number:
        digits = "".join(filter(str.isdigit, target_str))
        if len(digits) >= 10:
            phone_number = digits

    if not phone_number:
        wake_screen()
        run_adb('shell am start -a android.intent.action.VIEW "content://contacts/people"')
        return f"Contact {target} not saved, opening phone contacts, sir."

    clean_num = "".join(filter(str.isdigit, str(phone_number)))
    wake_screen()
    
    slot_id = 0 if sim_slot == 1 else 1
    cmd = (
        f'shell am start -a android.intent.action.CALL -d tel:{clean_num} '
        f'--ei simSlot {slot_id} --ei com.android.phone.extra.slot {slot_id} '
        f'--ei subscription {slot_id}'
    )
    res = run_adb(cmd)
    
    if "Error" in res or "SecurityException" in res:
        run_adb(f'shell am start -a android.intent.action.DIAL -d tel:{clean_num}')
        time.sleep(1)
        run_adb("shell input keyevent 5")

    return f"Calling {target} on SIM {sim_slot}, sir."

def play_youtube_on_phone(query):
    wake_screen()
    clean_q = query.strip()
    
    try:
        # Step 1: Fetch top Video ID(Bypass search ads completely)
        import urllib.request
        search_url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(clean_q)
        html = urllib.request.urlopen(search_url).read().decode()
        video_ids = re.findall(r"watch\?v=(\S{11})", html)
        
        if video_ids:
            top_video_id = video_ids[0]
            # Step 2: Launch Direct Video Link on Android YouTube
            cmd = f'shell am start -a android.intent.action.VIEW -d "vnd.youtube:{top_video_id}" com.google.android.youtube'
            run_adb(cmd)
            return f"Playing {clean_q} on your phone's YouTube app, sir."
    except Exception:
        pass

    # Fallback Direct Search Intent
    encoded = urllib.parse.quote(clean_q)
    cmd = f'shell am start -a android.intent.action.VIEW -d "https://www.youtube.com/results?search_query={encoded}" com.google.android.youtube'
    run_adb(cmd)
    return f"Opening {clean_q} on your YouTube app, sir."

def get_phone_battery():
    out = run_adb("shell dumpsys battery")
    for line in out.splitlines():
        if "level:" in line:
            level = line.split("level:")[1].strip()
            return f"Phone battery is at {level} percent, sir."
    return "Could not retrieve phone battery status."

def open_app_on_phone(app_name):
    apps = {
        "whatsapp": "com.whatsapp",
        "youtube": "com.google.android.youtube",
        "camera": "android.media.action.STILL_IMAGE_CAMERA",
        "spotify": "com.spotify.music",
        "instagram": "com.instagram.android"
    }
    pkg = apps.get(app_name.lower())
    if pkg:
        wake_screen()
        run_adb(f"shell monkey -p {pkg} -c android.intent.category.LAUNCHER 1")
        return f"Opening {app_name} on your phone, sir."
    return f"App {app_name} not configured."