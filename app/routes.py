from flask import request
from flask_cors import CORS
import time

movement_data = {
    "up/down": 1950,
    "left/right": 1950,
}

last_update_time = 0
TIMEOUT = 2

EXPECTED_KEYS = {
    "up/down": int,
    "left/right": int,
}

def register_routes(app):

    CORS(app, origins=["https://yourdomain.com"])  # restrict later

    @app.route("/movement", methods=["GET", "POST"])
    def movement():
        global movement_data, last_update_time

        if request.method == "POST":
            json_data = request.get_json()

            if not json_data:
                return {"error": "Invalid JSON"}, 400

            movement_data = {
                "up/down": max(0, min(json_data["up/down"], 4095)),
                "left/right": max(0, min(json_data["left/right"], 4095)),
            }

            last_update_time = time.time()
            return {"status": "ok"}

        if (time.time() - last_update_time) > TIMEOUT:
            print("Data timeout, resetting to zero")
            return {"up/down": 1950, "left/right": 1950, "status": "timeout"}

        return movement_data