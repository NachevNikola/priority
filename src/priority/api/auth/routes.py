from datetime import datetime, timezone
from flask import request, jsonify, current_app, Blueprint
from src.priority.extensions import db
from src.priority.errors import bad_request
from src.priority.api.users.models import User
import sqlalchemy as sa
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from .schemas import LoginInput, AccessTokensResponse
from src.priority.api import auth_service

auth = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    login_data = LoginInput.model_validate(data)

    tokens_data = auth_service.login(login_data)
    response_model = AccessTokensResponse.model_validate(tokens_data)

    return jsonify(response_model.model_dump()), 200


@auth.route('/token/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_access_token():
    user_id = int(get_jwt_identity())

    tokens_data = auth_service.refresh_token(user_id)
    response_model = AccessTokensResponse.model_validate(tokens_data)

    return jsonify(response_model.model_dump()), 200
