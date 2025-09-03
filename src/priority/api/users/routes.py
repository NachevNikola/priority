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
    """Register a new user.

    Creates a new user account with a unique username and email.
    The provided password will be stored hashed.
    A 409 Conflict error is returned if the username or email is already in use.
    """
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
    """Get current user profile.

    Retrieves the profile information for the currently authenticated user.
    """
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
    """Update current user profile.

    Updates the profile for the currently authenticated user.
    Only the fields provided in the request body will be changed.
    A 409 Conflict error is returned if the new username or email is already in use by another account.
    """
    user_id = int(get_jwt_identity())
    validated_data = request.context.json

    user = user_service.update(user_id, validated_data)

    response_model = UserResponse.model_validate(user)

    return jsonify(response_model.model_dump()), 200
