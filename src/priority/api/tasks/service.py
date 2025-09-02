from typing import List

from flask import abort
import sqlalchemy as sa

from .schemas import TaskCreateInput, TaskUpdateInput
from src.priority.api.users.models import User
from src.priority.extensions import db
from src.priority.core import PriorityCalculator
from .models import Task, Category, Tag

class TaskService:
    """
    Handles all business logic and database interactions for Tasks.
    Only allows for operations of objects related to a specific user,
    passed as a user_id argument to all methods.
    The methods return tasks with a calculated priority score.
    """

    def __init__(self, priority_calculator: PriorityCalculator):
        self.priority_calculator = priority_calculator

    def get_all(self, user_id: int) -> List[Task]:
        """Gets all user tasks with their priority scores."""
        user = db.get_or_404(User, user_id, description="User not found")

        for task in user.tasks:
            task.priority_score = self.priority_calculator.calculate_task_score(task)

        return user.tasks

    def create(self, user_id: int, task_data: TaskCreateInput) -> Task:
        """Creates a new task for the user."""
        task = Task(
            title=task_data.title,
            completed=task_data.completed,
            duration=task_data.duration_minutes,
            deadline=task_data.deadline,
            user_id=user_id,
        )

        if task_data.category:
            task.category = self._get_or_create_user_category(user_id, task_data.category)

        task.tags = self._get_or_create_user_tags(user_id, task_data.tags)
        task.priority_score = self.priority_calculator.calculate_task_score(task)

        db.session.add(task)
        db.session.commit()

        return task

    def get(self, user_id: int, task_id: int) -> Task:
        """
        Gets a task by id for the user
        Throws HTTPException if rule does not exist, or it belongs to another user.
        """
        task = db.session.scalar(
            sa.Select(Task).where(Task.id == task_id)
        )

        if task is None:
            abort(404, description="Task not found")

        if task.user_id != user_id:
            abort(403, description="Task belongs to another user")

        return task

    def get_with_priority_score(self, user_id: int, task_id: int) -> Task:
        """Get a task for a user and include the calculated priority score."""
        task = self.get(user_id, task_id)

        task.priority_score = self.priority_calculator.calculate_task_score(task)

        return task

    def update(self, user_id: int, task_id: int, task_data: TaskUpdateInput) -> Task:
        """
        Updates an existing task.
        Category and tags will be created in db if they don't exist.
        Tags will be replaced if specified.
        """
        task = self.get(user_id, task_id)

        update_data = task_data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            if key == 'duration':
                task.duration = update_data["duration_minutes"]
            elif key == 'category':
                task.category = None
                if value:
                    task.category = self._get_or_create_user_category(user_id, value)
            elif key == 'tags':
                task.tags.clear()
                task.tags = self._get_or_create_user_tags(user_id, value)
            else:
                setattr(task, key, value)

        task.priority_score = self.priority_calculator.calculate_task_score(task)
        db.session.add(task)
        db.session.commit()

        return task

    def complete(self, user_id:int, task_id: int):
        """Marks a task as completed for user."""
        task = self.get(user_id, task_id)
        task.completed = True
        task.priority_score = self.priority_calculator.calculate_task_score(task)

        db.session.add(task)
        db.session.commit()

        return task

    def delete(self, user_id: int, task_id: int):
        """Deletes a task for user."""
        task = self.get(user_id, task_id)

        db.session.delete(task)
        db.session.commit()

    def _get_or_create_user_category(self, user_id, category_name):
        """Finds a category by name for a user, or creates it if it doesn't exist."""
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

        return category

    def _get_or_create_user_tags(self, user_id, tag_names):
        """Finds tags by name for a user, or creates them if they don't exist."""
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

            tags.append(tag)

        return tags
