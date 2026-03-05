from flask import Flask
from flask_sock import Sock

sock = Sock()

def create_app():
    app = Flask(__name__)

    app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024

    sock.init_app(app)  # properly bind sock to app

    from .routes import register_routes
    register_routes(app, sock)  # pass sock into routes

    return app