"""Orbital Vitals backend: MediaPipe-based sleep / workout / consumption monitor."""
import math, os, threading, time
import cv2
import mediapipe as mp
import numpy as np
import uvicorn
from fastapi import FastAPI
from fastapi.responses import Response
from pydantic import BaseModel

CAMERA = int(os.getenv("CAMERA", 0))
SLEEP_ENTER_S = float(os.getenv("SLEEP_ENTER_S", 10))   # stillness needed to count as asleep
SLEEP_WAKE_S = float(os.getenv("SLEEP_WAKE_S", 5))      # disturbance needed to count as awake
REQUIRE_LYING = os.getenv("SLEEP_REQUIRE_LYING", "0") == "1"  # 0 = microgravity friendly
FOOD_GOAL, WATER_GOAL = 2800, 2500

mp_pose, mp_face, mp_draw = mp.solutions.pose, mp.solutions.face_mesh, mp.solutions.drawing_utils
L_EYE = [33, 160, 158, 133, 153, 144]
R_EYE = [362, 385, 387, 263, 373, 380]
KEY = [0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
# exercise: (left joints, right joints, flexed-below deg, extended-above deg, kcal/rep)
EXERCISES = {
    "squat": ((23, 25, 27), (24, 26, 28), 100, 160, 0.32),
    "pushup": ((11, 13, 15), (12, 14, 16), 90, 155, 0.45),
    "curl": ((11, 13, 15), (12, 14, 16), 50, 150, 0.15),
}


def angle(a, b, c):
    ba, bc = a - b, c - b
    cos = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc) + 1e-9)
    return math.degrees(math.acos(np.clip(cos, -1, 1)))


def eye_ratio(p, idx):  # eye aspect ratio (EAR)
    q = p[idx]
    return (np.linalg.norm(q[1] - q[5]) + np.linalg.norm(q[2] - q[4])) / (2 * np.linalg.norm(q[0] - q[3]) + 1e-9)


class Monitor:
    def __init__(self):
        self.lock = threading.Lock()
        self.jpg = b""
        self.exercise = "squat"
        self.reset()

    def reset(self):
        self.t_prev = self.prev = self.ear = None
        self.motion = 0.0
        self.posture = "unknown"
        self.sleeping, self.cand_since, self.wake_since = False, None, None
        self.sleep_s, self.movements, self.last_move = 0.0, 0, 0.0
        self.stage, self.work_kcal = "up", 0.0
        self.reps = {k: 0 for k in EXERCISES}
        self.food = self.water = self.intakes = 0
        self.mouth_since, self.latched = None, False

    # ---- analysis (call with lock held) ----
    def analyse(self, w, h, pose_res, face_res):
        now = time.time()
        dt = now - self.t_prev if self.t_prev else 0.0
        self.t_prev = now

        eyes = None  # True closed / False open / None unknown
        self.ear = None
        if face_res.multi_face_landmarks:
            fp = np.array([[l.x * w, l.y * h] for l in face_res.multi_face_landmarks[0].landmark])
            self.ear = float((eye_ratio(fp, L_EYE) + eye_ratio(fp, R_EYE)) / 2)
            eyes = self.ear < 0.2

        lm = pose_res.pose_landmarks.landmark if pose_res.pose_landmarks else None
        lying = False
        if lm:
            pts = np.array([[l.x * w, l.y * h] for l in lm])
            vis = np.array([l.visibility for l in lm])
            v = (pts[23] + pts[24]) / 2 - (pts[11] + pts[12]) / 2
            torso = np.linalg.norm(v) + 1e-6
            lying = abs(v[0]) > abs(v[1])
            self.posture = "lying" if lying else "upright"
            if self.prev is not None:
                m = np.mean(np.linalg.norm(pts[KEY] - self.prev[KEY], axis=1)) / torso
                self.motion = 0.8 * self.motion + 0.2 * m
            self.prev = pts
        else:
            self.posture, self.prev = "unknown", None
            self.motion *= 0.9

        # --- sleep: stillness + closed eyes (+ lying if required) ---
        cand = self.motion < 0.02 and (eyes is True or (REQUIRE_LYING and lying and eyes is None))
        if REQUIRE_LYING and not lying:
            cand = False
        if self.sleeping:
            self.sleep_s += dt
            if self.motion > 0.05 and now - self.last_move > 3:
                self.movements, self.last_move = self.movements + 1, now
            if cand:
                self.wake_since = None
            else:
                self.wake_since = self.wake_since or now
                if now - self.wake_since > SLEEP_WAKE_S:
                    self.sleeping, self.cand_since = False, None
        elif cand:
            self.cand_since = self.cand_since or now
            if now - self.cand_since >= SLEEP_ENTER_S:
                self.sleeping, self.wake_since = True, None
        else:
            self.cand_since = None

        if not lm or self.sleeping:
            self.mouth_since, self.latched = None, False
            return lm

        # --- workout: joint-angle rep counter ---
        lj, rj, lo, hi, kcal = EXERCISES[self.exercise]
        side = lj if vis[list(lj)].mean() >= vis[list(rj)].mean() else rj
        if vis[list(side)].min() > 0.5:
            a = angle(*pts[list(side)])
            if a < lo:
                self.stage = "down"
            elif a > hi and self.stage == "down":
                self.stage = "up"
                self.reps[self.exercise] += 1
                self.work_kcal += kcal

        # --- consumption: sustained hand-to-mouth gesture ---
        sw = np.linalg.norm(pts[11] - pts[12]) + 1e-6
        mouth = (pts[9] + pts[10]) / 2
        d = min((np.linalg.norm(pts[i] - mouth) / sw for i in (15, 16) if vis[i] > 0.5), default=9)
        if d < 0.45:
            self.mouth_since = self.mouth_since or now
            if now - self.mouth_since >= 0.6 and not self.latched:
                self.intakes, self.latched = self.intakes + 1, True
        else:
            self.mouth_since, self.latched = None, False
        return lm

    def snapshot(self):
        with self.lock:
            hrs = max(self.sleep_s / 3600, 0.05)
            return {
                "posture": self.posture,
                "motion": round(self.motion, 4),
                "sleep": {
                    "sleeping": self.sleeping, "total_s": round(self.sleep_s, 1),
                    "movements": self.movements, "ear": self.ear,
                    "quality": max(0, round(100 - self.movements / hrs * 4)),
                },
                "workout": {
                    "exercise": self.exercise, "reps": self.reps[self.exercise],
                    "total_reps": sum(self.reps.values()), "kcal": round(self.work_kcal, 1),
                },
                "consumption": {
                    "food_kcal": self.food, "water_ml": self.water,
                    "food_goal": FOOD_GOAL, "water_goal": WATER_GOAL, "detected_intakes": self.intakes,
                },
            }

    def store(self, frame):
        ok, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if ok:
            self.jpg = buf.tobytes()

    def run(self):
        cap = cv2.VideoCapture(CAMERA)
        with mp_pose.Pose(model_complexity=1, min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose, \
                mp_face.FaceMesh(max_num_faces=1) as face:
            while True:
                ok, frame = cap.read()
                if not ok:
                    frame = np.zeros((480, 640, 3), np.uint8)
                    cv2.putText(frame, "NO CAMERA SIGNAL", (150, 240), cv2.FONT_HERSHEY_SIMPLEX, 1, (80, 80, 255), 2)
                    self.store(frame)
                    time.sleep(0.5)
                    continue
                frame = cv2.flip(frame, 1)
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pr, fr = pose.process(rgb), face.process(rgb)
                with self.lock:
                    self.analyse(frame.shape[1], frame.shape[0], pr, fr)
                if pr.pose_landmarks:
                    mp_draw.draw_landmarks(frame, pr.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                s = self.snapshot()
                txt = "SLEEPING" if s["sleep"]["sleeping"] else f"{s['workout']['exercise']}: {s['workout']['reps']}"
                cv2.putText(frame, txt, (12, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 200, 80), 2)
                self.store(frame)


mon = Monitor()
app = FastAPI(title="Orbital Vitals")


@app.on_event("startup")
def _start():
    threading.Thread(target=mon.run, daemon=True).start()


@app.get("/api/state")
def state():
    return mon.snapshot()


@app.get("/frame.jpg")
def frame():
    return Response(mon.jpg, media_type="image/jpeg")


class Exercise(BaseModel):
    name: str


class Intake(BaseModel):
    kind: str  # "water" (ml) or "food" (kcal)
    amount: int


@app.post("/api/exercise")
def set_exercise(e: Exercise):
    if e.name in EXERCISES:
        with mon.lock:
            mon.exercise, mon.stage = e.name, "up"
    return {"ok": e.name in EXERCISES}


@app.post("/api/intake")
def add_intake(i: Intake):
    with mon.lock:
        if i.kind == "water":
            mon.water += i.amount
        elif i.kind == "food":
            mon.food += i.amount
    return {"ok": True}


@app.post("/api/reset")
def reset():
    with mon.lock:
        mon.reset()
    return {"ok": True}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
