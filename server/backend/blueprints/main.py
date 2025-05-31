from flask import Blueprint

main = Blueprint('main', __name__)

from server.backend.blueprints import auth, admin, play