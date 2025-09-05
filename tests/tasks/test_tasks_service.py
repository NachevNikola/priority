import pytest
from unittest.mock import Mock
from werkzeug.exceptions import NotFound, Forbidden

from src.priority.api.tasks.models import Task, Category, Tag
from src.priority.api.tasks.schemas import TaskCreateInput, TaskUpdateInput, TasksFilterParams
from src.priority.api.tasks.service import TaskService
from src.priority.api.users.models import User


class TestTaskService:

    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.db = db
        self.priority_calculator = Mock()
        self.priority_calculator.calculate_task_score.return_value = 50
        self.service = TaskService(self.priority_calculator)

        user1 = User(username="user1", email="user1@example.com")
        user2 = User(username="user2", email="user2@example.com")

        self.db.session.add_all([user1, user2])
        self.db.session.flush()

        category1 = Category(name="work", user_id=user1.id)
        tag1 = Tag(name="urgent", user_id=user1.id)

        task1 = Task(
            title="Task 1",
            completed=False,
            user_id=user1.id,
            category=category1,
            tags=[tag1]
        )
        task2 = Task(
            title="Task 2",
            completed=True,
            user_id=user1.id
        )
        task3 = Task(
            title="Task 3",
            completed=False,
            user_id=user2.id
        )

        self.db.session.add_all([category1, tag1, task1, task2, task3])
        self.db.session.commit()

        self.user1 = user1
        self.user2 = user2
        self.task1 = task1
        self.task2 = task2
        self.task3 = task3

    def test_create(self):
        task_input = TaskCreateInput(
            title="New Task",
            category="work",
            tags=["urgent"]
        )

        task_result = self.service.create(self.user1.id, task_input)

        assert task_result.title == "New Task"
        assert task_result.user_id == self.user1.id
        assert task_result.category.name == "work"
        assert len(task_result.tags) == 1
        assert task_result.priority_score == 50

    def test_get(self):
        task_result = self.service.get(self.user1.id, self.task1.id)

        assert task_result.id == self.task1.id
        assert task_result.title == self.task1.title

    def test_get_not_found(self):
        with pytest.raises(NotFound):
            self.service.get(self.user1.id, 999)

    def test_get_forbidden(self):
        with pytest.raises(Forbidden):
            self.service.get(self.user1.id, self.task3.id)

    def test_get_filtered(self):
        filters = TasksFilterParams(completed=False)

        tasks_result = self.service.get_filtered(self.user1.id, filters)

        assert len(tasks_result) == 1
        assert tasks_result[0].title == "Task 1"

    def test_update(self):
        update_input = TaskUpdateInput(
            title="Updated Task",
            completed=True
        )

        task_result = self.service.update(self.user1.id, self.task1.id, update_input)

        assert task_result.title == "Updated Task"
        assert task_result.completed is True

    def test_update_tags_replacement(self):
        update_input = TaskUpdateInput(tags=["new_tag"])

        task_result = self.service.update(self.user1.id, self.task1.id, update_input)

        assert len(task_result.tags) == 1
        assert task_result.tags[0].name == "new_tag"

    def test_complete(self):
        task_result = self.service.complete(self.user1.id, self.task1.id)

        assert task_result.completed is True

    def test_delete(self):
        task_id = self.task1.id

        self.service.delete(self.user1.id, task_id)

        with pytest.raises(NotFound):
            self.service.get(self.user1.id, task_id)

    def test_get_or_create_user_category_new(self):
        category_result = self.service._get_or_create_user_category(self.user1.id, "Personal")

        assert category_result.name == "personal"
        assert category_result.user_id == self.user1.id

    def test_get_or_create_user_tags_new(self):
        tags_result = self.service._get_or_create_user_tags(self.user1.id, ["new_tag"])

        assert len(tags_result) == 1
        assert tags_result[0].name == "new_tag"
