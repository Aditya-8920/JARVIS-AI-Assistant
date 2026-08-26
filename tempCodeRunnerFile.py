import cv2
import pyautogui
import numpy as np
import time
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import urllib.request
import os

SCREEN_W, SCREEN_H = pyautogui.size()
pyautogui.FAILSAFE = False

MODEL_PATH = "hand_landmarker.task"
if not os.path.exists(MODEL_PATH):
    print("[Downloading MediaPipe Hand Model...]")
    url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
    urllib.request.urlretrieve(url, MODEL_PATH)

base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.6,
    min_tracking_confidence=0.6
)
detector = vision.HandLandmarker.create_from_options(options)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

prev_x, prev_y = SCREEN_W // 2, SCREEN_H // 2
prev_scroll_y = 0
smoothening = 4
last_left_click = 0
last_right_click = 0

print("[Vision Pro Engine Complete]: Press 'q' to exit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape

    box_x1, box_y1 = 80, 40
    box_x2, box_y2 = w - 80, h - 80
    cv2.rectangle(frame, (box_x1, box_y1), (box_x2, box_y2), (0, 255, 0), 2)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    timestamp_ms = int(time.time() * 1000)

    results = detector.detect_for_video(mp_image, timestamp_ms)

    if results.hand_landmarks:
        for hand in results.hand_landmarks:
            idx_x, idx_y = int(hand[8].x * w), int(hand[8].y * h)
            mid_x, mid_y = int(hand[12].x * w), int(hand[12].y * h)
            thb_x, thb_y = int(hand[4].x * w), int(hand[4].y * h)

            dist_left = np.hypot(idx_x - thb_x, idx_y - thb_y)    # Index + Thumb
            dist_right = np.hypot(mid_x - thb_x, mid_y - thb_y)   # Middle + Thumb
            dist_scroll = np.hypot(idx_x - mid_x, idx_y - mid_y)  # Index + Middle

            # Visual markers
            cv2.circle(frame, (idx_x, idx_y), 7, (255, 0, 0), cv2.FILLED)
            cv2.circle(frame, (mid_x, mid_y), 7, (255, 0, 255), cv2.FILLED)
            cv2.circle(frame, (thb_x, thb_y), 7, (0, 255, 255), cv2.FILLED)

            # 1. SCROLL MODE (Index & Middle joined together, Thumb away)
            if dist_scroll < 30 and dist_left > 40:
                cv2.putText(frame, "SCROLL MODE", (40, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                if prev_scroll_y != 0:
                    delta_y = idx_y - prev_scroll_y
                    if abs(delta_y) > 6:
                        scroll_amount = int(-delta_y * 8)
                        pyautogui.scroll(scroll_amount)
                prev_scroll_y = idx_y

            # 2. CLICK & CURSOR MODE
            else:
                prev_scroll_y = 0
                screen_x = np.interp(idx_x, (box_x1, box_x2), (0, SCREEN_W))
                screen_y = np.interp(idx_y, (box_y1, box_y2), (0, SCREEN_H))

                curr_x = prev_x + (screen_x - prev_x) / smoothening
                curr_y = prev_y + (screen_y - prev_y) / smoothening
                pyautogui.moveTo(curr_x, curr_y)
                prev_x, prev_y = curr_x, curr_y

                # Left Click
                if dist_left < 30 and (time.time() - last_left_click > 0.4):
                    pyautogui.leftClick()
                    last_left_click = time.time()
                    cv2.putText(frame, "LEFT CLICK!", (40, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                # Right Click
                elif dist_right < 30 and (time.time() - last_right_click > 0.4):
                    pyautogui.rightClick()
                    last_right_click = time.time()
                    cv2.putText(frame, "RIGHT CLICK!", (40, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 165, 255), 2)

    cv2.putText(frame, "Index+Thumb: Left | Mid+Thumb: Right | 2 Fingers Join: Scroll",
                (15, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

    cv2.imshow("JARVIS MediaPipe HUD", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()