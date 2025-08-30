from flask import Blueprint, request, jsonify
import sqlalchemy as sa
from flask_jwt_extended import jwt_required, get_jwt_identity
from pydantic import ValidationError, TypeAdapter

from .models import Rule, Condition, User
from .extensions import db
from .errors import bad_request
from .schemas import RuleCreateModel, RuleUpdateModel, RuleResponse, RulesListResponse

rules = Blueprint('rules', __name__, url_prefix='/api/rules')


@rules.route('', methods=['GET'])
@jwt_required()
def get_rules():
    user_id = get_jwt_identity()
    user = db.get_or_404(User, user_id)

    response_model = RulesListResponse.model_validate({'rules': user.rules})

    return jsonify(response_model.model_dump()), 200

@rules.route('', methods=['POST'])
@jwt_required()
def create_rule():
    user_id = get_jwt_identity()
    json_data = request.get_json()

    try:
        rule_data = RuleCreateModel.model_validate(json_data)
    except ValidationError as e:
        return bad_request(e.errors())

    rule = Rule(
        name=rule_data.name,
        boost=rule_data.boost,
        user_id=user_id
    )

    for condition_data in rule_data.conditions:
        condition = Condition(
            field=condition_data.field,
            operator=condition_data.operator,
            value=condition_data.value
        )
        condition.rule = rule

    db.session.add(rule)
    db.session.commit()


    response_model = RuleResponse.model_validate(rule)
    return jsonify(response_model.model_dump()), 201

@rules.route('/<int:rule_id>', methods=['GET'])
@jwt_required()
def get_rule(rule_id):
    user_id = int(get_jwt_identity())

    rule = db.session.scalar(
        sa.Select(Rule).where(Rule.id == rule_id, Rule.user_id == user_id)
    )

    if rule is None:
        return bad_request('this rule does not exist')

    response_model = RuleResponse.model_validate(rule)

    return jsonify(response_model.model_dump()), 200

@rules.route('/<int:rule_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update(rule_id):
    user_id = get_jwt_identity()
    json_data = request.get_json()

    try:
        rule_data = RuleUpdateModel.model_validate(json_data)
    except ValidationError as e:
        return bad_request(e.errors())

    rule = db.session.scalar(
        sa.Select(Rule).where(Rule.id == rule_id, Rule.user_id == int(user_id))
    )

    if rule is None:
        return bad_request('this rule does not exist')

    update_data = rule_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        if key == "conditions":
            rule.conditions.clear()
            for condition_data in value:
                condition = Condition(
                    field=condition_data['field'],
                    operator=condition_data['operator'],
                    value=condition_data['value']
                )
                condition.rule = rule
        else:
            setattr(rule, key, value)

    db.session.add(rule)
    db.session.commit()

    response_model = RuleResponse.model_validate(rule)
    return jsonify(response_model.model_dump()), 201

@rules.route('/<int:rule_id>', methods=['DELETE'])
@jwt_required()
def delete_rule(rule_id):
    user_id = get_jwt_identity()

    rule = db.session.scalar(
        sa.Select(Rule).where(Rule.id == rule_id, Rule.user_id == user_id)
    )

    if rule is None:
        return bad_request('this rule does not exist')

    db.session.delete(rule)
    db.session.commit()

    return '', 204
