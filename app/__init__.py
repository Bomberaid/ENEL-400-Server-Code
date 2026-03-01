from flask import Flask

def create_app():
    app = Flask(__name__)

    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10MB upload limit

    from .routes import register_routes
    register_routes(app)

    return app