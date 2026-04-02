from flask import request
import time
import json

movement_data = {
    "up/down":    1950,
    "left/right": 1950,
    "kp":         2.0,
    "ki":         0.5,
    "kd":         0.1,
    "mode":       "NRF Mode"
}

car_data = {
    "speed":          0,
    "air":            "Good",
    "temperature":    25,
    "closest_object": "None Detected"
}

last_update_time = 0
TIMEOUT = 5
connected_clients = set()
car_data_clients  = set()

def register_routes(app, sock):

    # ── Controller → Server (writes movement_data) ────────────────────────────
    @sock.route("/ws_input")
    def input_ws(ws):
        global movement_data, last_update_time
        print("Controller connected via WebSocket")
        try:
            while True:
                data = ws.receive()
                if data:
                    parsed = json.loads(data)
                    movement_data["up/down"]    = max(0, min(int(parsed["up/down"]), 4095))
                    movement_data["left/right"] = max(0, min(int(parsed["left/right"]), 4095))
                    movement_data["kp"]         = float(parsed["kp"])
                    movement_data["ki"]         = float(parsed["ki"])
                    movement_data["kd"]         = float(parsed["kd"])
                    movement_data["mode"]       = str(parsed["mode"])
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

    # ── Car ESP32 → reads movement_data ──────────────────────────────────────
    @sock.route("/ws")
    def movement_ws(ws):
        global movement_data, last_update_time
        connected_clients.add(ws)
        print("Car ESP32 connected via WebSocket")

        try:
            while True:
                if (time.time() - last_update_time) > TIMEOUT:
                    ws.send(json.dumps({
                        "up/down":    1950,
                        "left/right": 1950,
                        "kp":         2.0,
                        "ki":         0.5,
                        "kd":         0.1,
                        "mode":       "NRF Mode",
                        "status":     "timeout"
                    }))
                ws.receive(timeout=TIMEOUT)

        except Exception as e:
            print(f"Car ESP32 disconnected: {e}")
        finally:
            connected_clients.discard(ws)

    # ── Car ESP32 → writes car_data ───────────────────────────────────────────
    @sock.route("/ws_car_input")
    def car_input_ws(ws):
        global car_data
        print("Car telemetry sender connected via WebSocket")
        try:
            while True:
                data = ws.receive()
                if data:
                    parsed = json.loads(data)
                    car_data["speed"]          = int(parsed["speed"])
                    car_data["air"]            = str(parsed["air"])
                    car_data["temperature"]    = int(parsed["temperature"])
                    car_data["closest_object"] = str(parsed["closest_object"])

                    dead_clients = set()
                    for client in car_data_clients:
                        try:
                            client.send(json.dumps(car_data))
                        except Exception:
                            dead_clients.add(client)
                    car_data_clients.difference_update(dead_clients)

        except Exception as e:
            print(f"Car telemetry sender disconnected: {e}")

    # ── Anyone → reads car_data ───────────────────────────────────────────────
    @sock.route("/ws_car")
    def car_ws(ws):
        global car_data
        car_data_clients.add(ws)
        print("Car data listener connected via WebSocket")

        try:
            ws.send(json.dumps(car_data))
            while True:
                ws.receive(timeout=30)

        except Exception as e:
            print(f"Car data listener disconnected: {e}")
        finally:
            car_data_clients.discard(ws)