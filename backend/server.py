"""(http://127.0.0.1:5000)
POST /api/veri = same as /sport or /consumed, chosen by the JSON you send (used by sports.java)
GET  /meals =3yemek
POST /consumed ={"slot": 0, "status": "true"}  (slot 0/1/2, status true/false/semi)
GET  /sport =today's squats and plank times (filled by sensor/back.py)
POST /sport =body {"type": "squat", "value": 1} or {"type": "plank", "value": 42.5}
"""
import json
import os
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
 
import meals
 
HOST, PORT = "127.0.0.1", 5000
SPORT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sport_history.txt")
 
# Pick today's meals once, when the server starts
todays = meals.select_meal()
eaten = set()  # slots already recorded, so a double click can't write twice
 
 
def load_sport_today():
    """Rebuild today's totals from sport_history.txt (tab separated: date, type, value)."""
    totals = {"squats": 0, "plank_total_seconds": 0.0, "plank_best_seconds": 0.0}
    try:
        with open(SPORT_FILE, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.rstrip("\n").split("\t")
                if len(parts) != 3 or parts[0] != str(date.today()):
                    continue
                try:
                    value = float(parts[2])
                except ValueError:
                    continue
                if parts[1] == "squat":
                    totals["squats"] += int(value)
                elif parts[1] == "plank":
                    totals["plank_total_seconds"] += value
                    totals["plank_best_seconds"] = max(totals["plank_best_seconds"], value)
    except FileNotFoundError:
        pass
    return totals
 
 
sport = load_sport_today()
 
 
def add_sport(kind, value):
    if kind == "squat":
        value = int(value)
        if value <= 0:
            raise ValueError("neg")
        sport["squats"] += value
    elif kind == "plank":
        value = float(value)
        if value <= 0:
            raise ValueError("neg")
        sport["plank_total_seconds"] += value
        sport["plank_best_seconds"] = max(sport["plank_best_seconds"], value)
    else:
        raise ValueError("type must be squat or plank")
    with open(SPORT_FILE, "a", encoding="utf-8") as f:
        f.write(f"{date.today()}\t{kind}\t{value}\n")
 
 
def meals_payload():
    out = []
    for slot, m in enumerate(todays):
        out.append({
            "slot": slot,
            "label": m[0],
            "protein": m[1],
            "vitamins": m[2],
            "energy": m[3],
            "name": m[4],
            "consumed": slot in eaten,
        })
    return {"meals": out}
 
 
class Handler(BaseHTTPRequestHandler):
    def _send(self, code, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
 
    def do_GET(self):
        if self.path == "/meals":
            self._send(200, meals_payload())
        elif self.path == "/sport":
            self._send(200, sport)
        else:
            self._send(404, {"error": "not found"})
 
    def do_POST(self):
        if self.path not in ("/consumed", "/sport", "/api/veri"):
            self._send(404, {"error": "not found"})
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length) or b"{}")
            # /api/veri is the address the Java client (sports.java) already uses.
            # It accepts both shapes: {"type":..,"value":..} (sport) or {"slot":..,"status":..} (meal)
            if self.path == "/sport" or (self.path == "/api/veri" and "type" in data):
                add_sport(str(data["type"]), data["value"])
                self._send(200, sport)
                return
            if self.path == "/api/veri" and "slot" not in data:
                raise ValueError('send {"type": "squat", "value": 1} or {"slot": 0, "status": "true"}')
            slot = int(data["slot"])
            status = str(data.get("status", "true"))
            if slot in eaten:
                self._send(409, {"error": "already recorded"})
                return
            meals.consumed(slot, status)
            eaten.add(slot)
            self._send(200, {"ok": True})
        except (KeyError, ValueError, TypeError, json.JSONDecodeError) as e:
            self._send(400, {"error": str(e)})
 
    def log_message(self, fmt, *args):
        print("[server]", fmt % args)
 
 
if __name__ == "__main__":
    print(f"Serving on http://{HOST}:{PORT}")
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()