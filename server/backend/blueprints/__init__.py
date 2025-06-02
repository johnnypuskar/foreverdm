from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO

socketio = SocketIO(cors_allowed_origins="*", ping_interval=10)

def create_app(debug = False):
    app = Flask(__name__)
    app.debug = debug
    CORS(app)

    from server.backend.blueprints.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    socketio.init_app(app)
    return app

    