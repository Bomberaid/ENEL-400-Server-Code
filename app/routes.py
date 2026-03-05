from flask import request
import time
import json

movement_data = {
    "up/down": 1950,
    "left/right": 1950,
}

last_update_time = 0
TIMEOUT = 2
connected_clients = set()

def register_routes(app, sock):

    @sock.route("/ws")
    def movement_ws(ws):
        global movement_data, last_update_time

        connected_clients.add(ws)
        print("ESP32 connected via WebSocket")

        try:
            while True:
                if (time.time() - last_update_time) > TIMEOUT:
                    ws.send(json.dumps({"up/down": 1950, "left/right": 1950, "status": "timeout"}))
                ws.receive(timeout=TIMEOUT)

        except Exception as e:
            print(f"ESP32 disconnected: {e}")
        finally:
            connected_clients.discard(ws)

    @app.route("/movement", methods=["POST"])
    def movement():
        global movement_data, last_update_time

        json_data = request.get_json()

        if not json_data:
            return {"error": "Invalid JSON"}, 400

        movement_data = {
            "up/down": max(0, min(json_data["up/down"], 4095)),
            "left/right": max(0, min(json_data["left/right"], 4095)),
        }

        last_update_time = time.time()

        dead_clients = set()
        for client in connected_clients:
            try:
                client.send(json.dumps(movement_data))
            except Exception:
                dead_clients.add(client)

        connected_clients.difference_update(dead_clients)

        return {"status": "ok"}