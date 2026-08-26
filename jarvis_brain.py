import os
import re
import sys
import time
import datetime
import asyncio
import subprocess
import edge_tts
import pygame
import pyautogui
import pywhatkit
import speech_recognition as sr
from groq import Groq
from config import GROQ_API_KEY

try:
    import system_tools
except ImportError:
    system_tools = None

try:
    import phone_bridge
except ImportError:
    phone_bridge = None

try:
    import assistant_tools
except ImportError:
    assistant_tools = None

client = Groq(api_key=GROQ_API_KEY)
VOICE = "en-GB-RyanNeural"
gesture_process = None

def pick_working_groq_model():
    try:
        all_models = client.models.list()
        for m in all_models.data:
            m_id = m.id.lower()
            if any(k in m_id for k in ["guard", "whisper", "orpheus", "vision", "compound"]):
                continue
            return m.id
    except Exception:
        pass
    return "llama-3.1-8b-instant"

ACTIVE_MODEL = pick_working_groq_model()
print(f"[System Model Active]: {ACTIVE_MODEL}")

async def _generate_audio(text, filename):
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(filename)

def speak(text):
    print(f"\n[JARVIS]: {text}")
    temp_file = f"voice_{int(time.time() * 1000)}.mp3"
    try:
        asyncio.run(_generate_audio(text, temp_file))
        pygame.mixer.init()
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.stop()
        pygame.mixer.quit()
    except Exception as e:
        print(f"[TTS Error]: {e}")
    finally:
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass

def start_gestures():
    global gesture_process
    if gesture_process is None or gesture_process.poll() is not None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        venv_py = os.path.join(script_dir, "jarvis_env", "Scripts", "python.exe")
        exec_path = venv_py if os.path.exists(venv_py) else sys.executable
        gesture_script = os.path.join(script_dir, "hand_controller.py")
        gesture_process = subprocess.Popen([exec_path, gesture_script])
        speak("Vision Pro hand gestures activated, sir.")
    else:
        speak("Hand gestures are already running, sir.")

def stop_gestures():
    global gesture_process
    if gesture_process and gesture_process.poll() is None:
        gesture_process.terminate()
        gesture_process = None
        speak("Hand gestures disabled, sir.")
    else:
        speak("Gesture tracking is not active, sir.")

def autonomous_brain(user_prompt):
    cmd = user_prompt.lower().strip()
    
    # 1. Vision Pro Hand Gestures
    if any(k in cmd for k in ["turn on hand gesture", "start gesture", "activate gesture", "enable gesture", "hand gesture on"]):
        start_gestures()
        return
    if any(k in cmd for k in ["turn off hand gesture", "stop gesture", "deactivate gesture", "disable gesture", "hand gesture off"]):
        stop_gestures()
        return

    # 2. Phone Calling
    if cmd.startswith("call") and phone_bridge:
        sim = 2 if ("sim 2" in cmd or "sim2" in cmd) else 1
        target_name = re.sub(r"(call|via\s*sim\s*\d|from\s*sim\s*\d|using\s*sim\s*\d|on\s*sim\s*\d|sim\s*\d|phone|mobile|please)", "", cmd, flags=re.IGNORECASE).strip()
        speak(phone_bridge.make_call(target_name, sim_slot=sim))
        return

    # 3. Phone YouTube & Apps
    if "youtube" in cmd and any(k in cmd for k in ["phone", "mobile", "yt"]) and phone_bridge:
        clean_song = re.sub(r"(play|on\s+my\s+phone's|on\s+my\s+phone|on\s+phone's|on\s+phone|on\s+youtube|youtube|yt|my\s+phone's|phone's|phone|'s)", "", cmd, flags=re.IGNORECASE).strip()
        speak(phone_bridge.play_youtube_on_phone(clean_song))
        return

    if any(k in cmd for k in ["open whatsapp", "open camera", "open instagram"]) and any(k in cmd for k in ["phone", "mobile"]) and phone_bridge:
        app = "whatsapp" if "whatsapp" in cmd else ("camera" if "camera" in cmd else "instagram")
        speak(phone_bridge.open_app_on_phone(app))
        return

    # 4. Assistant Utilities (Volume, Windows, Screenshot, Tab/App Switch, Weather)
    if assistant_tools:
        if any(k in cmd for k in ["volume up", "increase volume", "sound up"]):
            speak(assistant_tools.adjust_volume("up"))
            return
        if any(k in cmd for k in ["volume down", "decrease volume", "sound down"]):
            speak(assistant_tools.adjust_volume("down"))
            return
        if "mute" in cmd:
            speak(assistant_tools.adjust_volume("mute"))
            return
        if any(k in cmd for k in ["switch tab", "next tab", "change tab"]):
            speak(assistant_tools.manage_windows("tab"))
            return
        if any(k in cmd for k in ["switch window", "switch app", "next window", "change window"]):
            speak(assistant_tools.manage_windows("switch"))
            return
        if any(k in cmd for k in ["close window", "close this window", "close app", "close this app"]):
            speak(assistant_tools.manage_windows("close"))
            return
        if any(k in cmd for k in ["minimize", "show desktop", "minimize all"]):
            speak(assistant_tools.manage_windows("minimize"))
            return
        if any(k in cmd for k in ["take screenshot", "take a screenshot", "screenshot"]):
            speak(assistant_tools.take_screenshot())
            return
        if "paste to phone" in cmd and phone_bridge:
            speak(assistant_tools.sync_clipboard_to_phone(phone_bridge.run_adb))
            return
        if "weather" in cmd:
            speak(assistant_tools.get_live_weather())
            return
        if "timer" in cmd:
            digits = re.findall(r"\d+", cmd)
            secs = int(digits[0]) * 60 if digits else 60
            speak(assistant_tools.set_timer(secs, f"{secs//60} minutes", speak))
            return

    # 5. Diagnostics & System Stats
    if any(k in cmd for k in ["phone battery", "mobile battery", "cell battery", "phone charging"]) and phone_bridge:
        speak(phone_bridge.get_phone_battery())
        return
    if "battery" in cmd and system_tools:
        speak(system_tools.get_battery())
        return
    if any(k in cmd for k in ["cpu", "system report", "system status", "diagnostics"]) and system_tools:
        speak(system_tools.get_system_report())
        return

    # 6. PC Media & App Launchers
    if cmd.startswith("play "):
        song = cmd.replace("play ", "").strip()
        pywhatkit.playonyt(song)
        speak(f"Playing {song} on PC YouTube, sir.")
        return
    if cmd.startswith("open chrome") or cmd == "chrome":
        os.system("start chrome")
        speak("Opening Google Chrome, sir.")
        return
    if cmd.startswith("open notepad") or cmd == "notepad":
        os.system("start notepad")
        speak("Opening Notepad, sir.")
        return
    if cmd.startswith("open calc") or "calculator" in cmd:
        os.system("start calc")
        speak("Opening Calculator, sir.")
        return

    # 7. Conversational AI with Memory
    system_prompt = "You are JARVIS. Answer directly in 1-2 witty, crisp sentences. Maintain concise contextual dialogue."
    messages = [{"role": "system", "content": system_prompt}]
    
    # Append recent conversation history
    if assistant_tools:
        messages.extend(assistant_tools.CONVERSATION_HISTORY[-4:])
    messages.append({"role": "user", "content": user_prompt})

    try:
        response = client.chat.completions.create(
            model=ACTIVE_MODEL,
            messages=messages,
            temperature=0.3
        )
        reply = response.choices[0].message.content.strip()
        if assistant_tools:
            assistant_tools.CONVERSATION_HISTORY.append({"role": "user", "content": user_prompt})
            assistant_tools.CONVERSATION_HISTORY.append({"role": "assistant", "content": reply})
        speak(reply)
    except Exception as e:
        print(f"[LLM Error]: {e}")
        speak("Unable to process that right now, sir.")

def listen_microphone():
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = False
    
    is_awake = True
    print("\n==========================================")
    print(">>> JARVIS AUTONOMOUS SYSTEM ONLINE <<<")
    print("==========================================")
    speak("Jarvis is fully operational and standing by, sir.")
    
    with sr.Microphone() as source:
        while True:
            try:
                if is_awake:
                    print("\n[Active Listening...]")
                    audio = recognizer.listen(source, timeout=6, phrase_time_limit=7)
                    user_text = recognizer.recognize_google(audio).strip()
                    print(f"[Captured Audio]: {user_text}")
                    
                    # Sleep / Standby commands
                    if any(word in user_text.lower() for word in ["exit jarvis", "go to sleep", "sleep jarvis", "standby"]):
                        stop_gestures()
                        speak("Entering standby mode. Just say Hey Jarvis when you need me, sir.")
                        is_awake = False
                        continue
                        
                    # Complete Shutdown command (agar script sach me band karni ho)
                    if any(word in user_text.lower() for word in ["power off", "terminate system", "shutdown"]):
                        stop_gestures()
                        speak("Shutting down core systems. Goodbye, sir.")
                        time.sleep(2)
                        break
                    
                    cleaned_cmd = re.sub(r"^(hey jarvis|jarvis|ok jarvis)[,\s]*", "", user_text, flags=re.IGNORECASE).strip()
                    target_cmd = cleaned_cmd if cleaned_cmd else user_text
                    autonomous_brain(target_cmd)

                else:
                    # STANDBY SLEEP LOOP: Only listening for Wake Word
                    print("\n[Standby Mode - Listening for 'Hey Jarvis'...]")
                    audio = recognizer.listen(source, timeout=None, phrase_time_limit=4)
                    phrase = recognizer.recognize_google(audio).lower()
                    print(f"[Standby Audio]: {phrase}")
                    
                    if any(k in phrase for k in ["hey jarvis", "jarvis", "wake up", "are you there"]):
                        is_awake = True
                        speak("Online and ready, sir.")

            except sr.WaitTimeoutError:
                pass
            except sr.UnknownValueError:
                pass
            except Exception as e:
                print(f"[Mic Status]: {e}")

if __name__ == "__main__":
    listen_microphone()