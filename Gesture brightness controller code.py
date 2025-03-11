import cv2
import mediapipe as mp
import numpy as np
import serial
import time

# Initialize serial communication (Change 'COM3' to your Arduino port)
arduino = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)  # Give time for the connection to establish

# Initialize MediaPipe Hand tracking
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# Start video capture
cap = cv2.VideoCapture(0)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Flip image and convert to RGB
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process the frame
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Get landmarks for thumb and index finger
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
            index_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

            # Convert to pixel values
            h, w, _ = frame.shape
            thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)
            index_x, index_y = int(index_tip.x * w), int(index_tip.y * h)

            # Draw circles on fingertips
            cv2.circle(frame, (thumb_x, thumb_y), 10, (255, 0, 0), -1)
            cv2.circle(frame, (index_x, index_y), 10, (255, 0, 0), -1)

            # Calculate distance between thumb and index finger
            distance = np.linalg.norm([index_x - thumb_x, index_y - thumb_y])

            # Map distance to brightness (0-100)
            brightness = np.interp(distance, [30, 200], [0, 100])
            brightness = int(np.clip(brightness, 0, 100))

            # Send brightness value to Arduino
            arduino.write(f"{brightness}\n".encode())

            # Display brightness on screen
            cv2.putText(frame, f"Brightness: {brightness}%", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Show output
    cv2.imshow("Gesture Brightness Control", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
arduino.close()
