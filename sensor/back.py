import math
import time
 
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
 
POSE_MODEL_PATH = "pose_landmarker_lite.task"
 
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
 
# Body chains as (shoulder, hip, knee, ankle) for each side
LEFT_CHAIN = (11, 23, 25, 27)
RIGHT_CHAIN = (12, 24, 26, 28)
 
VIS_MIN = 0.5            # minimum landmark visibility to trust it
SQUAT_UP_ANGLE = 160     # knee angle above this = standing
SQUAT_DOWN_ANGLE = 100   # knee angle below this = bottom of squat
PLANK_BODY_ANGLE = 160   # shoulder-hip-ankle angle above this = straight body
PLANK_KNEE_ANGLE = 150   # knees must be mostly straight
PLANK_MAX_SLOPE = 0.35   # max (vertical / horizontal) shoulder-to-ankle ratio
PLANK_GRACE_FRAMES = 12  # bad frames tolerated before the timer resets
 
 
def angle(a, b, c):
    """Angle in degrees at point b, formed by points a-b-c."""
    ang = abs(math.degrees(
        math.atan2(c[1] - b[1], c[0] - b[0])
        - math.atan2(a[1] - b[1], a[0] - b[0])
    ))
    return 360 - ang if ang > 180 else ang
 
 
def vis(lm):
    return 1.0 if lm.visibility is None else lm.visibility
 
 
def format_time(seconds):
    return f"{int(seconds // 60):02d}:{seconds % 60:04.1f}"
 
 
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
 
#durum
mode = "squat"          # "squat" or "plank" (press s / p to switch)
reps = 0
stage = "up"            # squat stage
plank_start = None      # when the current plank hold began
plank_lost = 0          # consecutive frames the plank form was broken
best_hold = 0.0
 
while True:
    ret, frame = cap.read()
    if not ret:
        break
 
    frame = cv2.flip(frame, 1)
    h, w = frame.shape[:2]
 
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
 
    ts = int((time.monotonic() - start) * 1000)
    if ts <= last_ts:
        ts = last_ts + 1
    last_ts = ts
 
    pose_result = pose_landmarker.detect_for_video(mp_image, ts)
 
    knee_angle = None
    body_angle = None
    plank_ok = False
 
    # Full body (blue lines, yellow dots)
    for pose in pose_result.pose_landmarks:
        points = [(int(lm.x * w), int(lm.y * h)) for lm in pose]
        visible = [vis(lm) > VIS_MIN for lm in pose]
 
        for a, b in POSE_CONNECTIONS:
            if visible[a] and visible[b]:
                cv2.line(frame, points[a], points[b], (255, 0, 0), 3)
        for i, p in enumerate(points):
            if visible[i] and i not in SKIP_POINTS:
                cv2.circle(frame, p, 5, (0, 255, 255), -1)
 
        left_score = sum(vis(pose[i]) for i in LEFT_CHAIN)
        right_score = sum(vis(pose[i]) for i in RIGHT_CHAIN)
        chain = LEFT_CHAIN if left_score >= right_score else RIGHT_CHAIN
        sh, hip, knee, ank = chain
 
        if all(visible[i] for i in (hip, knee, ank)):
            knee_angle = angle(points[hip], points[knee], points[ank])
 
        if all(visible[i] for i in (sh, hip, ank)):
            body_angle = angle(points[sh], points[hip], points[ank])
 
        # squat
        if mode == "squat" and knee_angle is not None:
            if knee_angle < SQUAT_DOWN_ANGLE and stage == "up":
                stage = "down"
            elif knee_angle > SQUAT_UP_ANGLE and stage == "down":
                stage = "up"
                reps += 1
                print(f"Squats: {reps}")
 
        # plank
        if (
            mode == "plank"
            and body_angle is not None
            and knee_angle is not None
        ):
            dx = abs(points[ank][0] - points[sh][0])
            dy = abs(points[ank][1] - points[sh][1])
            horizontal = dx > 0 and (dy / dx) < PLANK_MAX_SLOPE
            plank_ok = (
                body_angle >= PLANK_BODY_ANGLE
                and knee_angle >= PLANK_KNEE_ANGLE
                and horizontal
            )
 
    #plank zaman
    if mode == "plank":
        if plank_ok:
            plank_lost = 0
            if plank_start is None:
                plank_start = time.monotonic()
        else:
            plank_lost += 1
            if plank_lost > PLANK_GRACE_FRAMES and plank_start is not None:
                held = time.monotonic() - plank_start
                best_hold = max(best_hold, held)
                plank_start = None
 
    hold = 0.0 if plank_start is None else time.monotonic() - plank_start
 
    #yazı
    cv2.putText(frame, f"Mode: {mode.upper()}  (s = squat, p = plank, q = quit)",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
 
    if mode == "squat":
        cv2.putText(frame, f"Squats: {reps}", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.1, (0, 255, 0), 3)
        cv2.putText(frame, f"Stage: {stage}", (10, 105),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        if knee_angle is not None:
            cv2.putText(frame, f"Knee angle: {knee_angle:.0f}", (10, 135),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)
    else:
        color = (0, 255, 0) if plank_start is not None else (0, 0, 255)
        cv2.putText(frame, f"Hold: {format_time(hold)}", (10, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.1, color, 3)
        cv2.putText(frame, f"Best: {format_time(best_hold)}", (10, 105),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        if body_angle is not None:
            cv2.putText(frame, f"Body angle: {body_angle:.0f}", (10, 135),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)
 
    cv2.imshow("Camera Feed", frame)
 
    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    elif key == ord("s") and mode != "squat":
        mode = "squat"
        reps, stage = 0, "up"
    elif key == ord("p") and mode != "plank":
        mode = "plank"
        plank_start, plank_lost = None, 0
 
pose_landmarker.close()
cap.release()
cv2.destroyAllWindows()