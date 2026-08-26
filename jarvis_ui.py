import os
import sys
import time
import threading
import psutil
import customtkinter as ctk

# Existing backend tools import
try:
    import jarvis_brain
except ImportError:
    jarvis_brain = None

try:
    import assistant_tools
except ImportError:
    assistant_tools = None

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class TextRedirector:
    """Redirects Python stdout/stderr directly into the CustomTkinter Textbox"""
    def __init__(self, textbox):
        self.textbox = textbox

    def write(self, text):
        if text.strip():
            self.textbox.after(0, self._append, text)

    def _append(self, text):
        self.textbox.insert("end", text + "\n")
        self.textbox.see("end")

    def flush(self):
        pass

class JarvisHUD(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("J.A.R.V.I.S. // AUTONOMOUS OS INTERFACE")
        self.geometry("900x620")
        self.minsize(800, 550)
        self.configure(fg_color="#0b0f19")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ==========================================
        # LEFT SIDEBAR - CONTROLS & TELEMETRY
        # ==========================================
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=15, fg_color="#111827")
        self.sidebar.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Logo / Title
        self.logo_label = ctk.CTkLabel(
            self.sidebar, 
            text="⚡ J.A.R.V.I.S.", 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#38bdf8"
        )
        self.logo_label.pack(pady=(20, 5))

        self.subtitle = ctk.CTkLabel(
            self.sidebar, 
            text="CORE SYSTEM ONLINE", 
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#10b981"
        )
        self.subtitle.pack(pady=(0, 20))

        # Telemetry - CPU
        self.cpu_label = ctk.CTkLabel(self.sidebar, text="CPU Usage: 0%", font=ctk.CTkFont(size=12))
        self.cpu_label.pack(anchor="w", padx=20, pady=(5, 0))
        self.cpu_bar = ctk.CTkProgressBar(self.sidebar, progress_color="#38bdf8", fg_color="#1e293b")
        self.cpu_bar.pack(fill="x", padx=20, pady=(2, 10))

        # Telemetry - RAM
        self.ram_label = ctk.CTkLabel(self.sidebar, text="RAM Usage: 0%", font=ctk.CTkFont(size=12))
        self.ram_label.pack(anchor="w", padx=20, pady=(5, 0))
        self.ram_bar = ctk.CTkProgressBar(self.sidebar, progress_color="#818cf8", fg_color="#1e293b")
        self.ram_bar.pack(fill="x", padx=20, pady=(2, 10))

        # Telemetry - Battery
        self.battery_label = ctk.CTkLabel(self.sidebar, text="Battery: 0%", font=ctk.CTkFont(size=12))
        self.battery_label.pack(anchor="w", padx=20, pady=(5, 0))
        self.battery_bar = ctk.CTkProgressBar(self.sidebar, progress_color="#34d399", fg_color="#1e293b")
        self.battery_bar.pack(fill="x", padx=20, pady=(2, 20))

        # Quick Control Buttons
        self.ctrl_title = ctk.CTkLabel(self.sidebar, text="QUICK ACTIONS", font=ctk.CTkFont(size=12, weight="bold"), text_color="#94a3b8")
        self.ctrl_title.pack(anchor="w", padx=20, pady=(10, 5))

        self.btn_gesture = ctk.CTkButton(
            self.sidebar, 
            text="🖐 Toggle Gestures", 
            command=self.toggle_gestures,
            fg_color="#1e293b", 
            hover_color="#334155"
        )
        self.btn_gesture.pack(fill="x", padx=20, pady=5)

        self.btn_screenshot = ctk.CTkButton(
            self.sidebar, 
            text="📸 Screenshot", 
            command=self.take_snap,
            fg_color="#1e293b", 
            hover_color="#334155"
        )
        self.btn_screenshot.pack(fill="x", padx=20, pady=5)

        self.btn_weather = ctk.CTkButton(
            self.sidebar, 
            text="🌤 Get Weather", 
            command=self.fetch_weather,
            fg_color="#1e293b", 
            hover_color="#334155"
        )
        self.btn_weather.pack(fill="x", padx=20, pady=5)

        # ==========================================
        # RIGHT MAIN PANEL - HUD & LIVE TERMINAL
        # ==========================================
        self.main_panel = ctk.CTkFrame(self, corner_radius=15, fg_color="#111827")
        self.main_panel.grid(row=0, column=1, padx=(0, 15), pady=15, sticky="nsew")
        self.main_panel.grid_rowconfigure(1, weight=1)
        self.main_panel.grid_columnconfigure(0, weight=1)

        # Central Visual Reactor Status
        self.hud_header = ctk.CTkFrame(self.main_panel, fg_color="transparent")
        self.hud_header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")

        self.orb_label = ctk.CTkLabel(
            self.hud_header, 
            text="●", 
            font=ctk.CTkFont(size=36), 
            text_color="#38bdf8"
        )
        self.orb_label.pack(side="left", padx=(5, 10))

        self.status_title = ctk.CTkLabel(
            self.hud_header, 
            text="VOICE ENGINE ACTIVE", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#f8fafc"
        )
        self.status_title.pack(side="left")

        # Live Console Output Box
        self.console = ctk.CTkTextbox(
            self.main_panel, 
            corner_radius=10, 
            fg_color="#030712", 
            text_color="#38bdf8", 
            font=ctk.CTkFont(family="Consolas", size=13)
        )
        self.console.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

        # Redirect prints into UI console box
        sys.stdout = TextRedirector(self.console)

        # Manual Command Input Box (Bottom)
        self.input_frame = ctk.CTkFrame(self.main_panel, fg_color="transparent")
        self.input_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")
        self.input_frame.grid_columnconfigure(0, weight=1)

        self.cmd_entry = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="Type a command or speak via microphone...", 
            height=40,
            fg_color="#1e293b",
            border_color="#334155"
        )
        self.cmd_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.cmd_entry.bind("<Return>", lambda e: self.send_manual_command())

        self.send_btn = ctk.CTkButton(
            self.input_frame, 
            text="Execute", 
            width=100, 
            height=40,
            command=self.send_manual_command,
            fg_color="#0284c7",
            hover_color="#0369a1"
        )
        self.send_btn.grid(row=0, column=1)

        # Initialize Background Threads
        self.gesture_active = False
        threading.Thread(target=self.telemetry_loop, daemon=True).start()
        threading.Thread(target=self.voice_listener_loop, daemon=True).start()

    def telemetry_loop(self):
        while True:
            try:
                cpu = psutil.cpu_percent()
                ram = psutil.virtual_memory().percent
                battery = psutil.sensors_battery()
                
                self.cpu_label.configure(text=f"CPU Usage: {cpu}%")
                self.cpu_bar.set(cpu / 100)

                self.ram_label.configure(text=f"RAM Usage: {ram}%")
                self.ram_bar.set(ram / 100)

                if battery:
                    self.battery_label.configure(text=f"Battery: {battery.percent}%")
                    self.battery_bar.set(battery.percent / 100)
            except Exception:
                pass
            time.sleep(2)

    def voice_listener_loop(self):
        if jarvis_brain:
            try:
                jarvis_brain.listen_microphone()
            except Exception as e:
                print(f"[Voice Error]: {e}")

    def send_manual_command(self):
        cmd = self.cmd_entry.get().strip()
        if not cmd:
            return
        self.cmd_entry.delete(0, "end")
        print(f"\n[USER]: {cmd}")
        
        if jarvis_brain:
            threading.Thread(target=jarvis_brain.autonomous_brain, args=(cmd,), daemon=True).start()

    def toggle_gestures(self):
        if not jarvis_brain:
            return
        if not self.gesture_active:
            jarvis_brain.start_gestures()
            self.btn_gesture.configure(fg_color="#059669")
            self.gesture_active = True
        else:
            jarvis_brain.stop_gestures()
            self.btn_gesture.configure(fg_color="#1e293b")
            self.gesture_active = False

    def take_snap(self):
        if assistant_tools:
            res = assistant_tools.take_screenshot()
            if jarvis_brain:
                jarvis_brain.speak(res)

    def fetch_weather(self):
        if assistant_tools:
            res = assistant_tools.get_live_weather()
            if jarvis_brain:
                jarvis_brain.speak(res)

if __name__ == "__main__":
    app = JarvisHUD()
    app.mainloop()