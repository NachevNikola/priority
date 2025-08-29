import os

SECRET_KEY = os.environ["SECRET_KEY"]

# SQLAlchemy.
pg_user = os.getenv("POSTGRES_USER", "priority")
pg_pass = os.getenv("POSTGRES_PASSWORD", "priority")
pg_host = os.getenv("POSTGRES_HOST", "postgres")
pg_port = os.getenv("POSTGRES_PORT", "5432")
pg_db = os.getenv("POSTGRES_DB", pg_user)
db = f"postgresql+psycopg://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_db}"
SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", db)
SQLALCHEMY_TRACK_MODIFICATIONS = False
