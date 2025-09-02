from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from spectree import SpecTree

# Instantiate the extensions
db = SQLAlchemy()
migrate = Migrate()

jwt_scheme = {
  "jwt": {
    "type": "http",
    "scheme": "bearer",
    "bearerFormat": "JWT"
  }
}
api = SpecTree(
    'flask',
    SECURITY_SCHEMES=[
        {
            "name": "jwt",
            "data": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "JWT"
            }
        }
    ]
)
