from dotenv import load_dotenv
from flask import Flask
from .auth import auth
from .tasks import tasks
from src.priority.extensions import migrate, db

load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config.from_object("src.config.settings")

    db.init_app(app)
    migrate.init_app(app, db)

    app.register_blueprint(auth)
    app.register_blueprint(tasks)

    return app

from src.priority.models import *
