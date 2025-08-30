from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.priority import db
from src.priority.errors import bad_request
from src.priority.models import Task, Category, Tag, User
from src.priority.schemas import TaskCreateInput, TaskUpdateInput, TaskResponse, TasksListResponse

import sqlalchemy as sa

from pydantic import ValidationError

from . import api


@api.route('/tasks/', methods=['GET'])
@jwt_required()
def get_tasks():
    user_id = int(get_jwt_identity())
    user = db.get_or_404(User, user_id)

    response_model = TasksListResponse.model_validate({'tasks': user.tasks})

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

    task = Task(
        title=task_data.title,
        completed=task_data.completed,
        duration=task_data.duration_minutes,
        deadline=task_data.deadline,
        user_id=user_id,
    )

    if task_data.category:
        task.category = get_or_create_user_category(user_id, task_data.category)

    task.tags = get_or_create_user_tags(user_id, task_data.tags)

    db.session.add(task)
    db.session.commit()

    response_model = TaskResponse.model_validate(task)
    return jsonify(response_model.model_dump(mode='json')), 201


@api.route('/tasks/<int:task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    user_id = int(get_jwt_identity())

    task = db.session.scalar(
        sa.Select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )

    if task is None:
        return bad_request('this task does not exist')

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

    task = db.session.scalar(
        sa.Select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )

    if task is None:
        return bad_request('this task does not exist')

    update_data = task_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        if key == 'duration':
            task.duration = update_data["duration_minutes"]
        elif key == 'category':
            task.category = None
            if value:
                task.category = get_or_create_user_category(user_id, value)
        elif key == 'tags':
            task.tags.clear()
            task.tags = get_or_create_user_tags(user_id, value)
        else:
            setattr(task, key, value)

    # user_rules = db.session.scalars(sa.select(Rule).where(Rule.user_id == user_id)).all()
    # task_to_update.priority_score = calculate_total_priority(task_to_update, user_rules)

    db.session.add(task)
    db.session.commit()
    response_model = TaskResponse.model_validate(task)
    return jsonify(response_model.model_dump(mode='json')), 201


@api.route('/tasks/<int:task_id>/complete', methods=['PUT', 'PATCH', 'POST'])
@jwt_required()
def complete_task(task_id):
    user_id = int(get_jwt_identity())

    task = db.session.scalar(
        sa.Select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )

    if task is None:
        return bad_request('this task does not exist')

    response_model = TaskResponse.model_validate(task)

    return jsonify(response_model.model_dump(mode='json')), 200

@api.route('/tasks/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    user_id = int(get_jwt_identity())

    task = db.session.scalar(
        sa.Select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )

    if task is None:
        return bad_request('this task does not exist')

    db.session.delete(task)
    db.session.commit()

    return '', 204


def get_or_create_user_category(user_id, category_name):
    category = db.session.scalar(
        sa.Select(Category).where(
            Category.user_id == user_id, Category.name == category_name
        )
    )
    if not category:
        category = Category(
            name=category_name.lower(),
            user_id=user_id,
        )
        db.session.add(category)
    return category

def get_or_create_user_tags(user_id, tag_names):
    tags = []
    for tag_name in tag_names:
        tag = db.session.scalar(
            sa.Select(Tag).where(
                Tag.user_id == user_id, Tag.name == tag_name
            )
        )
        if not tag:
            tag = Tag(
                name=tag_name,
                user_id=user_id,
            )
            db.session.add(tag)
        tags.append(tag)
    return tags
