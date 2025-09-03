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
    """List all prioritization rules.

    Retrieves a list of all prioritization rules and their associated
    conditions for the currently authenticated user.
    """
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
    """Create a new prioritization rule.

    Creates a new rule with a name, a priority boost value, and a list of
    one or more conditions. The new rule is automatically associated with
    the authenticated user.
    """
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
    """Retrieve a single rule by its ID.


    Fetches the details of a specific prioritization rule, including its
    list of conditions. Will return a 404 error if the rule does not
    exist or does, or a 403 if ti does not belong to the user.
    """
    user_id = int(get_jwt_identity())

    rule = rule_service.get(user_id, rule_id)

    response_model = RuleResponse.model_validate(rule)

    return jsonify(response_model.model_dump()), 200

@rules.route('/<int:rule_id>', methods=['PATCH'])
@jwt_required()
@api.validate(
    json=RuleUpdateInput,
    resp=Response(HTTP_200=RuleResponse, HTTP_401=None),
    security=[{'jwt': []}],
    tags=['rules']
)
def update_rule(rule_id):
    """Update an existing rule.

    Updates one or more attributes of a specific rule. Fields that are not
    included in the request body will remain unchanged. If the conditions
    list is given, it will fully replace the existing conditions for the rule.
    """
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
    """Delete a prioritization rule.

    Permanently deletes a specific rule and all of its associated conditions.
    """
    user_id = int(get_jwt_identity())

    rule_service.delete(user_id, rule_id)

    return "", 204
