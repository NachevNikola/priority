from flask import Flask
from .extensions import migrate, db
from src.priority.api.auth.routes import auth
from src.priority.api.users.routes import users
from src.priority.api.rules.routes import rules
from src.priority.api.tasks.routes import tasks
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
    app.register_blueprint(users)
    app.register_blueprint(rules)
    app.register_blueprint(tasks)
    app.register_blueprint(errors)

    return app

from src.priority.api.auth import routes
from src.priority.api.users import routes, models
from src.priority.api.rules import routes, models
from src.priority.api.tasks import routes, models
