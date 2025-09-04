from flask import Flask
from .extensions import migrate, db
from src.priority.api.auth.routes import auth
from src.priority.api.users.routes import users
from src.priority.api.rules.routes import rules
from src.priority.api.tasks.routes import tasks
from .errors import errors
from .extensions import api
from flask_jwt_extended import JWTManager

def create_app(override_settings=None):
    app = Flask(__name__)

    app.config.from_object("src.config.settings")
    if override_settings:
        app.config.update(override_settings)

    db.init_app(app)
    migrate.init_app(app, db)
    JWTManager(app)

    app.register_blueprint(auth)
    app.register_blueprint(users)
    app.register_blueprint(rules)
    app.register_blueprint(tasks)
    app.register_blueprint(errors)

    api.register(app)

    return app
