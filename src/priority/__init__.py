from flask import Flask
from .extensions import migrate, db
from .api import api
from .auth import auth
from .errors import errors
from .extensions import migrate, db
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)

    app.config.from_object("src.config.settings")

    db.init_app(app)
    migrate.init_app(app, db)
    JWTManager(app)

    app.register_blueprint(auth)
    app.register_blueprint(api)
    app.register_blueprint(errors)

    return app

from src.priority.models import *
