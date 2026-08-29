# ⚡ J.A.R.V.I.S. — Autonomous Multimodal AI Assistant

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![Groq](https://img.shields.io/badge/LLM-Groq%20API-orange.svg)
![OpenCV](https://img.shields.io/badge/Vision-OpenCV%20%7C%20MediaPipe-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Android%20Bridge-purple.svg)

An Iron Man–inspired, autonomous desktop assistant designed for low-latency voice execution, computer vision gesture control, Android device bridging via ADB, and full desktop automation.

---

## 🌟 Core Capabilities

* **Real-time Voice Intelligence:** Autonomous intent parsing and conversational generation powered by Groq LLM with contextual memory.
* **Vision Pro Gesture Tracking:** Contactless UI navigation using MediaPipe and OpenCV (pinch-to-click, virtual drag, and smart scrolling).
* **Android Hardware Bridge (ADB):** SIM-routed hands-free cellular calls, mobile app triggers, direct YouTube streaming on phone, and device telemetry.
* **Desktop & Web Automation:** Seamless media control, multi-window tiling, native/web application launcher (Spotify, Netflix, GitHub, etc.), and system diagnostics.
* **Cyberpunk HUD Dashboard:** CustomTkinter dark-mode graphical user interface featuring real-time conversation stream and resource monitoring.

---

## 🛠 Tech Stack

* **Core Language:** Python 3.10+
* **LLM Engine:** Groq API (`llama-3.1-8b-instant` / `llama-3.3-70b-versatile`)
* **Computer Vision:** OpenCV, MediaPipe
* **Speech Stack:** Google Speech Recognition, Microsoft Edge TTS (`edge-tts`), Pygame
* **Automation & Hardware Bridge:** Android Debug Bridge (ADB), PyAutoGUI, Pyperclip
* **GUI Engine:** CustomTkinter

---

## 🚀 Quick Setup & Installation

### 1. Clone the Repository
```bash
git clone [https://github.com/Aditya-8920/JARVIS-AI-Assistant.git](https://github.com/Aditya-8920/JARVIS-AI-Assistant.git)
cd JARVIS-AI-Assistant
```

### 2. Set Up Virtual Environment
```bash
python -m venv jarvis_env
.\jarvis_env\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a config.py file in the root project directory:
```bash
GROQ_API_KEY = "your_actual_groq_api_key_here"
```

### 5. Launch the Assistant
```bash
python jarvis_ui.py
```

## 🎙 Complete Voice & Gesture Commands Reference
###📱 Android Phone Bridge (ADB)

Call [Contact Name/Number] via SIM 1 / SIM 2 — Hands-free cellular calling via ADB.

Play [Song/Video Name] on phone YouTube — Direct deep-link playback on the mobile YouTube application.

Open WhatsApp / Camera / Instagram on phone — Launches corresponding apps on the target device.

Phone battery / Mobile battery — Live battery level and charging telemetry of connected phone.

Paste to phone — Transmits PC clipboard string directly to phone's active input field.

###🖐 Vision Pro Gesture Controls

Turn on hand gestures / Start gesture — Spawns webcam HUD and starts tracking pipeline.

Turn off hand gestures / Stop gesture — Safely terminates background tracking process.

Supported Gestures:

Index Finger Pinch / Tap: Virtual Cursor Click / Drag.

Two Fingers Up / Down: Smooth Screen Scrolling.

Open Palm / Fist: Minimize Active Window / Desktop HUD Toggle.

###🌐 Apps, Media & Web Controls

Open Spotify / Netflix / Instagram / ChatGPT / GitHub — Directly opens web player/portal in browser.

Open Chrome / Notepad / Calculator — Launches native Windows executable tools.

Play [Song Name] — Searches and plays high-definition audio on PC YouTube.

Volume up / Volume down / Mute — Step-by-step master audio adjustments.

Switch tab / Next tab — Cycles active web browser tabs (Ctrl + Tab).

Switch window / Switch app — Cycles running desktop applications (Alt + Tab).

Close window / Close app — Terminates focused active application window (Alt + F4).

Show desktop / Minimize all — Minimizes all open desktop windows (Win + D).

Take screenshot — Captures primary display and saves image inside Pictures folder.

Set a timer for [X] minutes — Asynchronous countdown timer with alert notification.

###⚡ System Diagnostics & State Management

Hey Jarvis / Wake up — Wake word detection from standby.

Go to sleep / Standby — Low-power background standby mode.

Shutdown / Power off — Complete session termination.

System report / CPU usage / Diagnostics — Real-time CPU, RAM, and thermals report.

Laptop battery — PC battery level and power plug status.

Weather — Live weather conditions and meteorological telemetry.

Any Query — Direct contextual conversational AI responses.




