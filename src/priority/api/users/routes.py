from flask import request, Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError

from src.priority.errors import bad_request
from src.priority.api import user_service
from .schemas import UserCreateInput, UserResponse, UserUpdateInput


users = Blueprint("users", __name__, url_prefix="/api/users")

@users.route('/', methods=['POST'])
def register():
    data = request.get_json()

    try:
        user_data = UserCreateInput.model_validate(data)
    except ValidationError as e:
        return bad_request(e.errors())

    user = user_service.register(user_data)

    response_model = UserResponse.model_validate(user)

    return jsonify(response_model.model_dump()), 201

@users.route('/me', methods=['GET'])
@jwt_required()
def get_user():
    user_id = int(get_jwt_identity())

    user = user_service.get(user_id)
    response_model = UserResponse.model_validate(user)

    return jsonify(response_model.model_dump()), 200

@users.route('/me', methods=['PUT'])
@jwt_required()
def update_user():
    user_id = int(get_jwt_identity())
    json_data = request.get_json()

    try:
        user_data = UserUpdateInput.model_validate(json_data)
    except ValidationError as e:
        return bad_request(e.errors())

    user = user_service.update(user_id, user_data)

    response_model = UserResponse.model_validate(user)

    return jsonify(response_model.model_dump()), 200
