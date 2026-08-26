import os
import sys
import subprocess
import speech_recognition as sr

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(SCRIPT_DIR, "jarvis_env", "Scripts", "python.exe")
EXEC = VENV_PYTHON if os.path.exists(VENV_PYTHON) else sys.executable
MAIN_BRAIN = os.path.join(SCRIPT_DIR, "jarvis_brain.py")

def start_continuous_wake_listener():
    recognizer = sr.Recognizer()
    recognizer.energy_threshold = 280
    recognizer.dynamic_energy_threshold = False
    
    print("[JARVIS BACKGROUND DAEMON]: Always listening for 'Hey Jarvis'...")
    
    with sr.Microphone() as source:
        while True:
            try:
                audio = recognizer.listen(source, timeout=None, phrase_time_limit=4)
                phrase = recognizer.recognize_google(audio).lower()
                
                if "jarvis" in phrase or "hey jarvis" in phrase or "wake up" in phrase:
                    print(f"\n[WAKE WORD DETECTED]: {phrase} -> Launching Jarvis Session...")
                    # Launches Jarvis brain session in dedicated process
                    p = subprocess.Popen([EXEC, MAIN_BRAIN])
                    p.wait() # Session khatam hone tak wait karega, fir wapas background listening
            except sr.UnknownValueError:
                pass
            except Exception:
                pass

if __name__ == "__main__":
    start_continuous_wake_listener()