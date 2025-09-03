from flask import request, Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from spectree import Response

from src.priority.api import user_service
from .schemas import UserCreateInput, UserResponse, UserUpdateInput
from src.priority.extensions import api


users = Blueprint("users", __name__, url_prefix="/api/users")

@users.route('/', methods=['POST'])
@api.validate(
    json=UserCreateInput,
    resp=Response(HTTP_201=UserResponse, HTTP_409=None, HTTP_401=None),
    tags=['users', 'auth']
)
def register():
    user = user_service.register(request.context.json)

    response_model = UserResponse.model_validate(user)

    return jsonify(response_model.model_dump()), 201

@users.route('/me', methods=['GET'])
@jwt_required()
@api.validate(
    resp=Response(HTTP_200=UserResponse, HTTP_401=None),
    security=[{'jwt': []}],
    tags=['users']
)
def get_user():
    user_id = int(get_jwt_identity())

    user = user_service.get(user_id)
    response_model = UserResponse.model_validate(user)

    return jsonify(response_model.model_dump()), 200

@users.route('/me', methods=['PUT'])
@jwt_required()
@api.validate(
    json=UserUpdateInput,
    resp=Response(HTTP_200=UserResponse, HTTP_401=None),
    security=[{'jwt': []}],
    tags=['users']
)
def update_user():
    user_id = int(get_jwt_identity())
    validated_data = request.context.json

    user = user_service.update(user_id, validated_data)

    response_model = UserResponse.model_validate(user)

    return jsonify(response_model.model_dump()), 200
