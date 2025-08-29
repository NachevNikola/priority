from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Instantiate the extensions
db = SQLAlchemy()
migrate = Migrate()
