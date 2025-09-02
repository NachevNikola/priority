from datetime import datetime, timezone
from flask import request, jsonify, current_app, Blueprint
from src.priority.extensions import db
from src.priority.errors import bad_request
from src.priority.api.users.models import User
import sqlalchemy as sa
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity


auth = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if 'email' not in data or 'password' not in data:
        return bad_request('must include email and password fields')

    user = db.session.scalar(
        sa.select(User).where(User.email == data['email'])
    )

    authenticated = user and user.check_password(data['password'])

    if not authenticated:
        return bad_request('Incorrect email or password')

    return generate_access_refresh_token(str(user.id))


@auth.route('/token/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_access_token():
    identity = get_jwt_identity()

    return generate_access_refresh_token(identity)


def generate_access_refresh_token(identity):
    access_token = create_access_token(identity=identity)
    refresh_token = create_refresh_token(identity=identity)

    access_time_delta = current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
    refresh_time_delta = current_app.config["JWT_REFRESH_TOKEN_EXPIRES"]

    now = datetime.now(timezone.utc)
    access_expires_at = (now + access_time_delta).isoformat()
    refresh_expires_at = (now + refresh_time_delta).isoformat()

    return jsonify(
        {
            'access_token': access_token,
            'access_token_expires_at': access_expires_at,
            'refresh_token': refresh_token,
            'refresh_token_expires_at': refresh_expires_at,
        }
    )
