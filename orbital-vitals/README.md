# Orbital Vitals

Crew health monitor: **JavaFX** front end + **Python (FastAPI + MediaPipe)** back end.

| Module | How it works |
|---|---|
| Sleep | MediaPipe Pose motion + Face Mesh eye-aspect-ratio. Still + eyes closed for 10 s = asleep; counts movements, estimates quality. |
| Workout | Pose joint angles drive a rep counter (squat / pushup / curl) with a kcal estimate. |
| Consumption | Detects sustained hand-to-mouth gestures; food (kcal) and water (ml) are logged with UI buttons against daily goals. |

## Run
```bash
# 1) backend (Python 3.9-3.11 recommended for mediapipe)
cd backend
./setup.sh               # Debian/Ubuntu: creates .venv with Python 3.11 (no system pip needed)
.venv/bin/python app.py  # http://127.0.0.1:8000  (CAMERA=1 to pick another webcam)

# 2) frontend (sudo apt install openjdk-17-jdk maven)
cd frontend
mvn javafx:run
```

Env vars: `SLEEP_ENTER_S`, `SLEEP_WAKE_S`, `SLEEP_REQUIRE_LYING=1` (use on Earth; default 0 suits microgravity sleep), `VITALS_API` (frontend backend URL).

API: `GET /api/state`, `GET /frame.jpg`, `POST /api/exercise`, `POST /api/intake`, `POST /api/reset`.
