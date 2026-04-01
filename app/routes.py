from flask import request
import time
import json

movement_data = {
    "up/down": 1950,
    "left/right": 1950,
    "speed": 0,
    "air": "Good",
    "temperature": 25,
    "kp": 2.0,
    "ki": 0.5,
    "kd": 0.1,
}

last_update_time = 0
TIMEOUT = 5
connected_clients = set()

def register_routes(app, sock):

    @sock.route("/ws_input")
    def input_ws(ws):
        global movement_data, last_update_time
        print("Controller connected via WebSocket")
        try:
            while True:
                data = ws.receive()
                if data:
                    parsed = json.loads(data)
                    movement_data["up/down"] = max(0, min(int(parsed["up/down"]), 4095))
                    movement_data["left/right"] = max(0, min(int(parsed["left/right"]), 4095))
                    movement_data["speed"] = int(parsed["speed"])
                    movement_data["air"] = parsed["air"]
                    movement_data["temperature"] = int(parsed["temperature"])
                    movement_data["kp"] = float(parsed["kp"])
                    movement_data["ki"] = float(parsed["ki"])
                    movement_data["kd"] = float(parsed["kd"])
                    last_update_time = time.time()

                    dead_clients = set()
                    for client in connected_clients:
                        try:
                            client.send(json.dumps(movement_data))
                        except Exception:
                            dead_clients.add(client)
                    connected_clients.difference_update(dead_clients)

        except Exception as e:
            print(f"Controller disconnected: {e}")

    @sock.route("/ws")
    def movement_ws(ws):
        global movement_data, last_update_time
        connected_clients.add(ws)
        print("Car ESP32 connected via WebSocket")

        try:
            while True:
                if (time.time() - last_update_time) > TIMEOUT:
                    ws.send(json.dumps({"up/down": 1950, "left/right": 1950, "speed": 0, "air": "Good", "temperature": 25, "kp": 2.0, "ki": 0.5, "kd": 0.1, "status": "timeout"}))
                ws.receive(timeout=TIMEOUT)

        except Exception as e:
            print(f"Car ESP32 disconnected: {e}")
        finally:
            connected_clients.discard(ws)