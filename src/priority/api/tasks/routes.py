from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from .schemas import TaskCreateInput, TaskUpdateInput, TaskResponse, TasksListResponse

from src.priority.errors import bad_request


from pydantic import ValidationError

from src.priority.api import api, task_service


@api.route('/tasks/', methods=['GET'])
@jwt_required()
def get_tasks():
    user_id = int(get_jwt_identity())

    tasks = task_service.get_all(user_id)

    response_model = TasksListResponse.model_validate({'tasks': tasks})

    return jsonify(response_model.model_dump(mode='json')), 200

@api.route('/tasks/', methods=['POST'])
@jwt_required()
def create_task():
    user_id = int(get_jwt_identity())
    json_data = request.get_json()

    try:
        task_data = TaskCreateInput.model_validate(json_data)
    except ValidationError as e:
        return bad_request(e.errors())

    task = task_service.create(user_id, task_data)

    response_model = TaskResponse.model_validate(task)

    return jsonify(response_model.model_dump(mode='json')), 201

@api.route('/tasks/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    user_id = int(get_jwt_identity())

    task = task_service.get_with_score(user_id, task_id)
    response_model = TaskResponse.model_validate(task)

    return jsonify(response_model.model_dump(mode='json')), 200

@api.route('/tasks/<int:task_id>', methods=['PUT', 'PATCH'])
@jwt_required()
def update_task(task_id):
    user_id = int(get_jwt_identity())
    json_data = request.get_json()

    try:
        task_data = TaskUpdateInput.model_validate(json_data)
    except ValidationError as e:
        return bad_request(e.errors())

    task = task_service.update(user_id, task_id, task_data)

    response_model = TaskResponse.model_validate(task)

    return jsonify(response_model.model_dump(mode='json')), 201

@api.route('/tasks/<int:task_id>/complete', methods=['PUT', 'PATCH', 'POST'])
@jwt_required()
def complete_task(task_id):
    user_id = int(get_jwt_identity())

    task = task_service.complete(user_id, task_id)

    response_model = TaskResponse.model_validate(task)

    return jsonify(response_model.model_dump(mode='json')), 200

@api.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    user_id = int(get_jwt_identity())

    task_service.delete(user_id, task_id)

    return '', 204
