import os
import time
import threading
import pyautogui
import pyperclip
import requests
import webbrowser

CONVERSATION_HISTORY = []

COMMON_WEB_APPS = {
    "spotify": "https://open.spotify.com",
    "youtube": "https://www.youtube.com",
    "instagram": "https://www.instagram.com",
    "whatsapp": "https://web.whatsapp.com",
    "netflix": "https://www.netflix.com",
    "chatgpt": "https://chat.openai.com",
    "github": "https://www.github.com",
    "reddit": "https://www.reddit.com",
    "twitter": "https://www.x.com",
    "x": "https://www.x.com",
    "prime video": "https://www.primevideo.com/",
    "jio hotstar": "https://www.hotstar.com/in/home",
    "gemini": "https://gemini.google.com/app",
    "chat gpt": "https://chatgpt.com/"
}

def open_app(app_name):
    name = app_name.lower().strip()
    
    # 1. Check popular web applications
    for key, url in COMMON_WEB_APPS.items():
        if key in name:
            webbrowser.open(url)
            return f"Opening {key.capitalize()}, sir."

    # 2. Check Windows local desktop apps
    try:
        if "chrome" in name:
            os.system("start chrome")
        elif "notepad" in name:
            os.system("start notepad")
        elif "calc" in name or "calculator" in name:
            os.system("start calc")
        elif "cmd" in name or "terminal" in name:
            os.system("start cmd")
        else:
            try:
                os.system(f"start {name}")
            except Exception:
                webbrowser.open(f"https://www.{name}.com")
        return f"Launching {app_name}, sir."
    except Exception as e:
        return f"Unable to open {app_name}: {e}"

def adjust_volume(level="up"):
    if level == "up":
        for _ in range(5):
            pyautogui.press("volumeup")
            time.sleep(0.05)
    elif level == "down":
        for _ in range(5):
            pyautogui.press("volumedown")
            time.sleep(0.05)
    elif level == "mute":
        pyautogui.press("volumemute")
    return f"Volume {level}, sir."

def manage_windows(action="minimize"):
    if "minimize" in action or "desktop" in action:
        pyautogui.hotkey("win", "d")
        return "Desktop shown, sir."
    elif "close" in action:
        pyautogui.keyDown("alt")
        pyautogui.press("f4")
        pyautogui.keyUp("alt")
        return "Active window closed, sir."
    elif "tab" in action:
        pyautogui.keyDown("ctrl")
        pyautogui.press("tab")
        pyautogui.keyUp("ctrl")
        return "Switched browser tab, sir."
    elif "switch" in action or "window" in action:
        pyautogui.keyDown("alt")
        pyautogui.press("tab")
        pyautogui.keyUp("alt")
        return "Switched application, sir."
    return "Action executed, sir."

def take_screenshot():
    timestamp = int(time.time())
    pictures_dir = os.path.join(os.path.expanduser("~"), "Pictures")
    if not os.path.exists(pictures_dir):
        os.makedirs(pictures_dir)
    shot_path = os.path.join(pictures_dir, f"jarvis_snap_{timestamp}.png")
    screenshot = pyautogui.screenshot()
    screenshot.save(shot_path)
    return "Screenshot captured and saved to Pictures, sir."

def _timer_worker(seconds, label, callback_speak):
    time.sleep(seconds)
    callback_speak(f"Alert: Timer for {label} is up, sir.")

def set_timer(seconds, label, callback_speak):
    t = threading.Thread(target=_timer_worker, args=(seconds, label, callback_speak), daemon=True)
    t.start()
    return f"Timer set for {label}, sir."

def sync_clipboard_to_phone(run_adb_func):
    text = pyperclip.paste()
    if not text:
        return "Clipboard is empty, sir."
    formatted = text.replace(" ", "%s").replace("\n", "%s")
    run_adb_func(f"shell input text {formatted}")
    return "Clipboard text pasted to device, sir."

def get_live_weather(city="Bhopal"):
    try:
        url = f"https://wttr.in/{city}?format=3"
        headers = {"User-Agent": "curl/7.68.0"}
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200 and res.text.strip():
            return f"Weather report: {res.text.strip()}, sir."
    except Exception as e:
        print(f"[Weather Error]: {e}")
    return "Unable to retrieve current weather, sir."