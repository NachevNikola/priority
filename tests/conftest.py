import pytest
from sqlalchemy_utils import database_exists, create_database, drop_database
from src.config import settings
from src.priority import create_app

@pytest.fixture(scope="session")
def app():
    db_uri = settings.SQLALCHEMY_DATABASE_URI + "_test"
    test_settings = {
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": db_uri,
    }
    app = create_app(override_settings=test_settings)
    return app

@pytest.fixture(scope="function")
def client(app):
    return app.test_client()

@pytest.fixture(scope="function")
def db(app):
    from src.priority.extensions import db
    with app.app_context():
        db_uri = app.config.get("SQLALCHEMY_DATABASE_URI")
        if not database_exists(db_uri):
            create_database(db_uri)

        db.drop_all()
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()
