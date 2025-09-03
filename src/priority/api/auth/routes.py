from flask import request, jsonify, Blueprint
from spectree import Response

from flask_jwt_extended import jwt_required, get_jwt_identity
from .schemas import LoginInput, AccessTokensResponse
from src.priority.api import auth_service
from src.priority.extensions import api
auth = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth.route('/login', methods=['POST'])
@api.validate(
    json=LoginInput,
    resp=Response(HTTP_200=AccessTokensResponse, HTTP_401=None),
    tags=['auth']
)
def login():
    """User Login.

    Authenticates a user with the email and password provided.
    If successful, it returns access and refresh JSON Web Tokens with their expiration date times.
    The access token is required for accessing resources on other endpoints.
    """
    validated_data = request.context.json

    tokens_data = auth_service.login(validated_data)
    response_model = AccessTokensResponse.model_validate(tokens_data)

    return jsonify(response_model.model_dump()), 200


@auth.route('/token/refresh', methods=['POST'])
@jwt_required(refresh=True)
@api.validate(
    resp=Response(HTTP_200=AccessTokensResponse, HTTP_401=None),
    security=[{'jwt': []}],
    tags=['auth']
)
def refresh_access_token():
    """Refresh access and refresh tokens.

    Generates new access and refresh tokens if a valid refresh token is used in the Authorization header.
    """
    user_id = int(get_jwt_identity())

    tokens_data = auth_service.refresh_token(user_id)
    response_model = AccessTokensResponse.model_validate(tokens_data)

    return jsonify(response_model.model_dump()), 200
