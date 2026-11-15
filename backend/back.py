import time
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

HAND_MODEL_PATH = "hand_landmarker.task"
POSE_MODEL_PATH = "pose_landmarker_lite.task"

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),
    (0, 5), (5, 6), (6, 7), (7, 8),
    (5, 9), (9, 10), (10, 11), (11, 12),
    (9, 13), (13, 14), (14, 15), (15, 16),
    (13, 17), (17, 18), (18, 19), (19, 20),
    (0, 17),
]

# Full body: face, torso, arms, legs
POSE_CONNECTIONS = [
    # face
    (0, 1), (1, 2), (2, 3), (3, 7), (0, 4), (4, 5), (5, 6), (6, 8), (9, 10),
    # shoulders and arms
    (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),
    # torso
    (11, 23), (12, 24), (23, 24),
    # left leg
    (23, 25), (25, 27), (27, 29), (29, 31), (27, 31),
    # right leg
    (24, 26), (26, 28), (28, 30), (30, 32), (28, 32),
]

SKIP_POINTS = {17, 18, 19, 20, 21, 22}

hand_options = vision.HandLandmarkerOptions(
    base_options=python.BaseOptions(model_asset_path=HAND_MODEL_PATH),
    running_mode=vision.RunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5,
)
hand_landmarker = vision.HandLandmarker.create_from_options(hand_options)

pose_options = vision.PoseLandmarkerOptions(
    base_options=python.BaseOptions(model_asset_path=POSE_MODEL_PATH),
    running_mode=vision.RunningMode.VIDEO,
    num_poses=1,
    min_pose_detection_confidence=0.5,
    min_pose_presence_confidence=0.5,
    min_tracking_confidence=0.5,
)
pose_landmarker = vision.PoseLandmarker.create_from_options(pose_options)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Can't open camera.")
    exit()

start = time.monotonic()
last_ts = -1

left_was_up = False
right_was_up = False

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h, w = frame.shape[:2]

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)

    # Timestamp in ms must strictly increase every frame
    ts = int((time.monotonic() - start) * 1000)
    if ts <= last_ts:
        ts = last_ts + 1
    last_ts = ts

    hand_result = hand_landmarker.detect_for_video(mp_image, ts)
    pose_result = pose_landmarker.detect_for_video(mp_image, ts)

    left_up = False
    right_up = False

    # Hands (green lines, red dots)
    for hand in hand_result.hand_landmarks:
        points = [(int(lm.x * w), int(lm.y * h)) for lm in hand]
        for a, b in HAND_CONNECTIONS:
            cv2.line(frame, points[a], points[b], (0, 255, 0), 2)
        for p in points:
            cv2.circle(frame, p, 4, (0, 0, 255), -1)

    # Full body (blue lines, yellow dots)
    for pose in pose_result.pose_landmarks:
        points = [(int(lm.x * w), int(lm.y * h)) for lm in pose]
        visible = [(lm.visibility is None or lm.visibility > 0.5) for lm in pose]

        for a, b in POSE_CONNECTIONS:
            if visible[a] and visible[b]:
                cv2.line(frame, points[a], points[b], (255, 0, 0), 3)
        for i, p in enumerate(points):
            if visible[i] and i not in SKIP_POINTS:
                cv2.circle(frame, p, 5, (0, 255, 255), -1)

        # Arm raised: wrist clearly above shoulder
        margin = 0.05 * h

        left_up = (
            visible[11] and visible[15]
            and points[15][1] < points[11][1] - margin
        )
        right_up = (
            visible[12] and visible[16]
            and points[16][1] < points[12][1] - margin
        )

    # Print once at the moment an arm goes up
    if left_up and not left_was_up:
        print(0)
    if right_up and not right_was_up:
        print(0)

    left_was_up = left_up
    right_was_up = right_up

    cv2.imshow("Camera Feed", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

hand_landmarker.close()
pose_landmarker.close()
cap.release()
cv2.destroyAllWindows()