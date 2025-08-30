from datetime import datetime, timezone
from flask import request, jsonify, current_app
from src.priority.extensions import db
from src.priority.errors import bad_request
from src.priority.models import User
import sqlalchemy as sa
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from . import auth

@auth.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return bad_request('must include username, email and password fields')
    if db.session.scalar(sa.select(User).where(
            User.username == data['username'])):
        return bad_request('please use a different username')
    if db.session.scalar(sa.select(User).where(
            User.email == data['email'])):
        return bad_request('please use a different email address')
    user = User()
    user.from_dict(data, new_user=True)
    db.session.add(user)
    db.session.commit()
    return user.to_dict(), 201


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
