from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError

from .schemas import RuleCreateInput, RuleUpdateInput, RuleResponse, RulesListResponse
from src.priority.errors import bad_request
from src.priority.api import rule_service


rules = Blueprint("rules", __name__, url_prefix="/api/rules")

@rules.route('/', methods=['GET'])
@jwt_required()
def get_rules():
    user_id = int(get_jwt_identity())

    rules = rule_service.get_all(user_id)

    response_model = RulesListResponse.model_validate({'rules': rules})

    return jsonify(response_model.model_dump()), 200

@rules.route('/', methods=['POST'])
@jwt_required()
def create_rule():
    user_id = int(get_jwt_identity())
    json_data = request.get_json()

    try:
        rule_data = RuleCreateInput.model_validate(json_data)
    except ValidationError as e:
        return bad_request(e.errors())

    rule = rule_service.create(user_id, rule_data)

    response_model = RuleResponse.model_validate(rule)
    return jsonify(response_model.model_dump()), 201

@rules.route('/<int:rule_id>', methods=['GET'])
@jwt_required()
def get_rule(rule_id):
    user_id = int(get_jwt_identity())

    rule = rule_service.get(user_id, rule_id)

    response_model = RuleResponse.model_validate(rule)

    return jsonify(response_model.model_dump()), 200

@rules.route('/<int:rule_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_rule(rule_id):
    user_id = int(get_jwt_identity())
    json_data = request.get_json()

    try:
        rule_data = RuleUpdateInput.model_validate(json_data)
    except ValidationError as e:
        return bad_request(e.errors())

    rule = rule_service.update(user_id, rule_id, rule_data)

    response_model = RuleResponse.model_validate(rule)
    return jsonify(response_model.model_dump()), 201

@rules.route('/<int:rule_id>', methods=['DELETE'])
@jwt_required()
def delete_rule(rule_id):
    user_id = int(get_jwt_identity())

    rule_service.delete(user_id, rule_id)

    return "", 204
