import pytest
from datetime import datetime, timedelta
from flask_jwt_extended import create_access_token
from tests.test_utils import make_request
from src.priority.api.tasks.models import Task, Category, Tag
from src.priority.api.users.models import User


class TestTasksRoutes:

    @pytest.fixture(autouse=True)
    def setup(self, app, client, db):
        self.app = app
        self.client = client

        user1 = User(username="user1", email="user1@example.com")
        user2 = User(username="user2", email="user2@example.com")

        category1 = Category(name="work", user_id=1)
        category2 = Category(name="personal", user_id=2)

        tag1 = Tag(name="urgent", user_id=1)
        tag2 = Tag(name="important", user_id=1)
        tag3 = Tag(name="low", user_id=2)

        task1 = Task(
            title="Complete project",
            completed=False,
            duration=timedelta(hours=2),
            deadline=datetime(2025, 9, 15, 10, 0),
            user_id=1,
            category=category1,
            tags=[tag1, tag2]
        )
        task2 = Task(
            title="Review code",
            completed=True,
            duration=timedelta(minutes=30),
            user_id=1,
            category=category1,
            tags=[tag1]
        )
        task3 = Task(
            title="Buy groceries",
            completed=False,
            user_id=2,
            category=category2,
            tags=[tag3]
        )

        db.session.add_all([user1, user2, category1, category2, tag1, tag2, tag3, task1, task2, task3])
        db.session.commit()

        self.user1 = user1
        self.user2 = user2
        self.task1 = task1
        self.task2 = task2
        self.task3 = task3

        self.user1_token = create_access_token(identity=str(1))
        self.user2_token = create_access_token(identity=str(2))

    def test_get_tasks_success(self):
        response = make_request(
            self.client,
            "GET",
            "/api/tasks/",
            token=self.user1_token
        )

        assert response.status_code == 200
        tasks_result = response.get_json()

        assert 'tasks' in tasks_result
        assert len(tasks_result['tasks']) == 2

        task_titles = [task['title'] for task in tasks_result['tasks']]
        assert self.task1.title in task_titles
        assert self.task2.title in task_titles

    def test_get_tasks_unauthorized(self):
        response = make_request(
            self.client,
            "GET",
            "/api/tasks/"
        )

        assert response.status_code == 401

    def test_get_tasks_with_filter(self):
        response = make_request(
            self.client,
            "GET",
            "/api/tasks/?completed=true",
            token=self.user1_token
        )

        assert response.status_code == 200
        task_result = response.get_json()

        assert len(task_result['tasks']) == 1
        assert task_result['tasks'][0]['title'] == self.task2.title
        assert task_result['tasks'][0]['completed'] == True


    def test_create_task(self):
        task_data = {
            'title': 'New task',
            'completed': False,
            'duration': 'PT1H30M',
            'deadline': '2025-09-20T15:30:00',
            'category': 'work',
            'tags': ['urgent', 'new']
        }

        response = make_request(
            self.client,
            "POST",
            "/api/tasks/",
            token=self.user1_token,
            data=task_data
        )

        assert response.status_code == 201
        task_result = response.get_json()

        assert task_result['title'] == 'New task'
        assert task_result['completed'] == False
        assert task_result['category']['name'] == 'work'
        assert len(task_result['tags']) == 2
        assert 'priority_score' in task_result

    def test_create_task_minimal(self):
        task_data = {
            'title': 'Simple task'
        }

        response = make_request(
            self.client,
            "POST",
            "/api/tasks/",
            token=self.user1_token,
            data=task_data
        )

        assert response.status_code == 201
        data = response.get_json()

        assert data['title'] == 'Simple task'
        assert data['completed'] == False
        assert data['category'] is None
        assert data['tags'] == []

    def test_create_task_invalid_data(self):
        # missing title field
        task_data = {
            'completed': False
        }

        response = make_request(
            self.client,
            "POST",
            "/api/tasks/",
            token=self.user1_token,
            data=task_data
        )

        assert response.status_code == 422

    def test_get_task_success(self):
        response = make_request(
            self.client,
            "GET",
            f"/api/tasks/{self.task1.id}",
            token=self.user1_token
        )

        assert response.status_code == 200
        task_response = response.get_json()

        assert task_response['id'] == self.task1.id
        assert task_response['title'] == self.task1.title
        assert task_response['completed'] == self.task1.completed
        assert 'priority_score' in task_response

    def test_get_task_not_found(self):
        response = make_request(
            self.client,
            "GET",
            "/api/tasks/999",
            token=self.user1_token
        )

        assert response.status_code == 404

    def test_get_task_forbidden(self):
        response = make_request(
            self.client,
            "GET",
            f"/api/tasks/{self.task3.id}",
            token=self.user1_token
        )

        assert response.status_code == 403

    def test_get_task_unauthorized(self):
        response = make_request(
            self.client,
            "GET",
            f"/api/tasks/{self.task1.id}"
        )

        assert response.status_code == 401

    def test_update_task(self):
        update_data = {
            'title': 'Updated task',
            'completed': True,
            'category': 'personal'
        }

        response = make_request(
            self.client,
            "PATCH",
            f"/api/tasks/{self.task1.id}",
            token=self.user1_token,
            data=update_data
        )

        assert response.status_code == 201
        task_response = response.get_json()

        assert task_response['title'] == update_data['title']
        assert task_response['completed'] == update_data['completed']
        assert task_response['category']['name'] == update_data['category']

    def test_update_task_with_tags(self):
        update_data = {
            'tags': ['new-tag', 'another-tag']
        }

        response = make_request(
            self.client,
            "PATCH",
            f"/api/tasks/{self.task1.id}",
            token=self.user1_token,
            data=update_data
        )

        assert response.status_code == 201
        task_response = response.get_json()

        assert len(task_response['tags']) == 2
        tag_names = [tag['name'] for tag in task_response['tags']]
        assert 'new-tag' in tag_names
        assert 'another-tag' in tag_names

    def test_complete_task(self):
        response = make_request(
            self.client,
            "POST",
            f"/api/tasks/{self.task1.id}/complete",
            token=self.user1_token
        )

        assert response.status_code == 200
        task_response = response.get_json()

        assert task_response['completed'] == True
        assert task_response['id'] == self.task1.id

    def test_delete_task_success(self):
        task_id = self.task1.id

        response = make_request(
            self.client,
            "DELETE",
            f"/api/tasks/{task_id}",
            token=self.user1_token
        )

        assert response.status_code == 204
        assert response.data == b''

        response = make_request(
            self.client,
            "GET",
            f"/api/tasks/{task_id}",
            token=self.user1_token
        )
        assert response.status_code == 404
