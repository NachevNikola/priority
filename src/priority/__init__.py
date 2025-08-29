from flask import Flask
from .auth import auth
from .tasks import tasks
from .errors import errors
from .me import me
from src.priority.extensions import migrate, db
from flask_jwt_extended import JWTManager

def create_app():
    app = Flask(__name__)

    app.config.from_object("src.config.settings")

    db.init_app(app)
    migrate.init_app(app, db)
    JWTManager(app)

    app.register_blueprint(auth)
    app.register_blueprint(tasks)
    app.register_blueprint(errors)
    app.register_blueprint(me)

    return app

from src.priority.models import *
