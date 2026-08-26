import cv2
import mediapipe as mp
import pyautogui
import numpy as np
import time

SCREEN_W, SCREEN_H = pyautogui.size()
pyautogui.FAILSAFE = False

# MediaPipe Hands Setup
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    max_num_hands=1,
    min_detection_confidence=0.75,
    min_tracking_confidence=0.75
)

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
if not cap.isOpened():
    cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

prev_x, prev_y = SCREEN_W // 2, SCREEN_H // 2
smoothening = 3
last_click_time = 0

print("[Vision Pro Engine]: Online. Pinch index+thumb to click. 'q' to quit.")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    
    # Active gesture box
    cv2.rectangle(frame, (100, 50), (540, 380), (0, 255, 0), 2)

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            
            # Landmark 8 = Index Tip, Landmark 4 = Thumb Tip
            idx_x = int(hand_landmarks.landmark[8].x * w)
            idx_y = int(hand_landmarks.landmark[8].y * h)
            thb_x = int(hand_landmarks.landmark[4].x * w)
            thb_y = int(hand_landmarks.landmark[4].y * h)

            # Map Index finger to Screen resolution
            screen_x = np.interp(idx_x, (100, 540), (0, SCREEN_W))
            screen_y = np.interp(idx_y, (50, 380), (0, SCREEN_H))

            # Smooth cursor movement
            curr_x = prev_x + (screen_x - prev_x) / smoothening
            curr_y = prev_y + (screen_y - prev_y) / smoothening
            
            pyautogui.moveTo(curr_x, curr_y)
            prev_x, prev_y = curr_x, curr_y

            # Draw visual tracking circles
            cv2.circle(frame, (idx_x, idx_y), 8, (255, 0, 0), cv2.FILLED)
            cv2.circle(frame, (thb_x, thb_y), 8, (0, 255, 255), cv2.FILLED)
            cv2.line(frame, (idx_x, idx_y), (thb_x, thb_y), (255, 255, 0), 2)

            # Pinch distance calculation (Euclidean Distance)
            distance = np.hypot(idx_x - thb_x, idx_y - thb_y)
            
            # Center point of pinch
            mid_x, mid_y = (idx_x + thb_x) // 2, (idx_y + thb_y) // 2

            # Vision Pro Pinch-Tap Trigger
            if distance < 30:
                cv2.circle(frame, (mid_x, mid_y), 12, (0, 255, 0), cv2.FILLED)
                if time.time() - last_click_time > 0.4:
                    pyautogui.click()
                    last_click_time = time.time()
                    cv2.putText(frame, "PINCH CLICK!", (50, 50), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

    cv2.imshow("JARVIS Vision HUD", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()