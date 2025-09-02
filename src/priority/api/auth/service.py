from datetime import datetime, timezone
from flask import current_app
from werkzeug.exceptions import Unauthorized

from src.priority.extensions import db
from src.priority.api.users.models import User
import sqlalchemy as sa
from flask_jwt_extended import create_access_token, create_refresh_token

from .schemas import LoginInput


class AuthService:

    def login(self, login_data: LoginInput):
        """
        Verifies that a user with the given email and password is in db.
        Returns JWT if authentication succeeded.
        """
        user = db.session.scalar(
            sa.select(User).where(User.email == login_data.email)
        )

        authenticated = user and user.check_password(login_data.password)

        if not authenticated:
            raise Unauthorized("Incorrect email or password.")

        return self._generate_access_refresh_token(str(user.id))

    def refresh_token(self, user_id: str):
        """Returns new set of access and refresh tokens."""
        return self._generate_access_refresh_token(str(user_id))

    def _generate_access_refresh_token(self, user_id: str):
        """
        Generates new access and refresh tokens for the given user.
        Also returns their expiration datetimes.
        """
        access_token = create_access_token(identity=user_id)
        refresh_token = create_refresh_token(identity=user_id)

        access_time_delta = current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
        refresh_time_delta = current_app.config["JWT_REFRESH_TOKEN_EXPIRES"]

        now = datetime.now(timezone.utc)
        access_expires_at = (now + access_time_delta).isoformat()
        refresh_expires_at = (now + refresh_time_delta).isoformat()

        return {
            'access_token': access_token,
            'access_token_expires_at': access_expires_at,
            'refresh_token': refresh_token,
            'refresh_token_expires_at': refresh_expires_at,
            }
