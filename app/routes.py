from flask import request
from flask_sock import Sock
import time
import json

movement_data = {
    "up/down": 1950,
    "left/right": 1950,
    "kp": 2.0,
    "ki": 0.5,
    "kd": 0.1,
}

last_update_time = 0
TIMEOUT = 2

connected_clients = set()

def register_routes(app):
    sock = Sock(app)

    @app.route("/movement", methods=["POST"])
    def movement():
        global movement_data, last_update_time

        json_data = request.get_json()

        if not json_data:
            return {"error": "Invalid JSON"}, 400

        movement_data = {
            "up/down": max(0, min(json_data["up/down"], 4095)),
            "left/right": max(0, min(json_data["left/right"], 4095)),
            "kp": json_data["kp"],
            "ki": json_data["ki"],
            "kd": json_data["kd"],
        }

        last_update_time = time.time()

        # Push to all connected ESP32 clients
        dead_clients = set()
        for client in connected_clients:
            try:
                client.send(json.dumps(movement_data))
            except Exception:
                dead_clients.add(client)

        connected_clients.difference_update(dead_clients)

        return {"status": "ok"}

    @sock.route("/ws")
    def movement_ws(ws):
        global movement_data, last_update_time

        connected_clients.add(ws)
        print("ESP32 connected via WebSocket")

        try:
            while True:
                # Handle timeout — push neutral values if controller goes silent
                if (time.time() - last_update_time) > TIMEOUT:
                    ws.send(json.dumps({"up/down": 1950, "left/right": 1950, "kp": 2.0, "ki": 0.5, "kd": 0.1, "status": "timeout"}))

                # Keep connection alive / receive any incoming messages
                ws.receive(timeout=TIMEOUT)

        except Exception:
            print("ESP32 disconnected")
        finally:
            connected_clients.discard(ws)