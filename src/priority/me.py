from src.priority.models import User
from flask import Blueprint, request
from .extensions import db
import sqlalchemy as sa
from .errors import bad_request
from flask_jwt_extended import jwt_required, get_jwt_identity

me = Blueprint('me', __name__, url_prefix='/api/me')


@me.route('', methods=['GET'])
@jwt_required()
def get_user():
    user_id = get_jwt_identity()
    return db.get_or_404(User, user_id).to_dict()

@me.route('', methods=['PUT'])
@jwt_required()
def update_user():
    user_id = get_jwt_identity()
    user = db.get_or_404(User, user_id)
    data = request.get_json()
    if 'username' in data and data['username'] != user.username and \
            db.session.scalar(sa.select(User).where(
                User.username == data['username'])):
        return bad_request('please use a different username')
    if 'email' in data and data['email'] != user.email and \
            db.session.scalar(sa.select(User).where(
                User.email == data['email'])):
        return bad_request('please use a different email address')
    user.from_dict(data, new_user=False)
    db.session.commit()
    return user.to_dict()
