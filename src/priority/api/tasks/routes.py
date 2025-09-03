from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from spectree import Response

from .schemas import TaskCreateInput, TaskUpdateInput, TaskResponse, TasksListResponse, TasksFilterParams

from src.priority.api import task_service
from src.priority.extensions import api

tasks = Blueprint("tasks", __name__, url_prefix="/api/tasks")

@tasks.route('/', methods=['GET'])
@jwt_required()
@api.validate(
    query=TasksFilterParams,
    resp=Response(HTTP_200=TasksListResponse, HTTP_401=None),
    security=[{'jwt': []}],
    tags=['tasks']
)
def get_tasks():
    user_id = int(get_jwt_identity())

    validated_query = request.context.query

    tasks = task_service.get_filtered(user_id,validated_query)

    response_model = TasksListResponse.model_validate({'tasks': tasks})

    return jsonify(response_model.model_dump(mode='json')), 200

@tasks.route('/', methods=['POST'])
@jwt_required()
@api.validate(
    json=TaskCreateInput,
    resp=Response(HTTP_200=TaskResponse, HTTP_401=None),
    security=[{'jwt': []}],
    tags=['tasks']
)
def create_task():
    user_id = int(get_jwt_identity())
    validated_data = request.context.json

    task = task_service.create(user_id, validated_data)

    response_model = TaskResponse.model_validate(task)

    return jsonify(response_model.model_dump(mode='json')), 201

@tasks.route('/<int:task_id>', methods=['GET'])
@jwt_required()
@api.validate(
    resp=Response(HTTP_200=TaskResponse, HTTP_401=None),
    security=[{'jwt': []}],
    tags=['tasks']
)
def get_task(task_id):
    user_id = int(get_jwt_identity())

    task = task_service.get_with_score(user_id, task_id)
    response_model = TaskResponse.model_validate(task)

    return jsonify(response_model.model_dump(mode='json')), 200

@tasks.route('/<int:task_id>', methods=['PUT', 'PATCH'])
@jwt_required()
@api.validate(
    json=TaskUpdateInput,
    resp=Response(HTTP_201=TaskResponse, HTTP_401=None),
    security=[{'jwt': []}],
    tags=['tasks']
)
def update_task(task_id):
    user_id = int(get_jwt_identity())
    validated_data = request.context.json

    task = task_service.update(user_id, task_id, validated_data)

    response_model = TaskResponse.model_validate(task)

    return jsonify(response_model.model_dump(mode='json')), 201

@tasks.route('/<int:task_id>/complete', methods=['PUT', 'PATCH', 'POST'])
@jwt_required()
@api.validate(
    resp=Response(HTTP_200=TaskResponse, HTTP_401=None),
    security=[{'jwt': []}],
    tags=['tasks']
)
def complete_task(task_id):
    user_id = int(get_jwt_identity())

    task = task_service.complete(user_id, task_id)

    response_model = TaskResponse.model_validate(task)

    return jsonify(response_model.model_dump(mode='json')), 200

@tasks.route('/<int:task_id>', methods=['DELETE'])
@jwt_required()
@api.validate(
    resp=Response(HTTP_204=None, HTTP_401=None),
    security=[{'jwt': []}],
    tags=['tasks']
)
def delete_task(task_id):
    user_id = int(get_jwt_identity())

    task_service.delete(user_id, task_id)

    return '', 204
