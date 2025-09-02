from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from spectree import Response

from .schemas import RuleCreateInput, RuleUpdateInput, RuleResponse, RulesListResponse
from src.priority.api import rule_service
from src.priority.extensions import api

rules = Blueprint("rules", __name__, url_prefix="/api/rules")

@rules.route('/', methods=['GET'])
@jwt_required()
@api.validate(
    resp=Response(HTTP_200=RulesListResponse, HTTP_401=None),
    security=[{'jwt': []}],
    tags=['rules']
)
def get_rules():
    user_id = int(get_jwt_identity())

    rules = rule_service.get_all(user_id)

    response_model = RulesListResponse.model_validate({'rules': rules})

    return jsonify(response_model.model_dump()), 200

@rules.route('/', methods=['POST'])
@jwt_required()
@api.validate(
    json=RuleCreateInput,
    resp=Response(HTTP_201=RuleResponse, HTTP_401=None),
    security=[{'jwt': []}],
    tags=['rules']
)
def create_rule():
    user_id = int(get_jwt_identity())
    validated_data = request.context.json

    rule = rule_service.create(user_id, validated_data)

    response_model = RuleResponse.model_validate(rule)
    return jsonify(response_model.model_dump()), 201

@rules.route('/<int:rule_id>', methods=['GET'])
@jwt_required()
@api.validate(
    resp=Response(HTTP_200=RuleResponse, HTTP_401=None),
    security=[{'jwt': []}],
    tags=['rules']
)
def get_rule(rule_id):
    user_id = int(get_jwt_identity())

    rule = rule_service.get(user_id, rule_id)

    response_model = RuleResponse.model_validate(rule)

    return jsonify(response_model.model_dump()), 200

@rules.route('/<int:rule_id>', methods=['PUT', 'PATCH'])
@jwt_required()
@api.validate(
    json=RuleUpdateInput,
    resp=Response(HTTP_200=RuleResponse, HTTP_401=None),
    security=[{'jwt': []}],
    tags=['rules']
)
def update_rule(rule_id):
    user_id = int(get_jwt_identity())
    validated_data = request.context.json

    rule = rule_service.update(user_id, rule_id, validated_data)

    response_model = RuleResponse.model_validate(rule)
    return jsonify(response_model.model_dump()), 200

@rules.route('/<int:rule_id>', methods=['DELETE'])
@jwt_required()
@api.validate(
    resp=Response(HTTP_204=None, HTTP_401=None),
    security=[{'jwt': []}],
    tags=['rules']
)
def delete_rule(rule_id):
    user_id = int(get_jwt_identity())

    rule_service.delete(user_id, rule_id)

    return "", 204
