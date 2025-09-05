import pytest
from flask_jwt_extended import create_access_token
from tests.test_utils import make_request
from src.priority.api.users.models import User


class TestUsersRoutes:

    @pytest.fixture(autouse=True)
    def setup(self, app, client, db):
        self.app = app
        self.client = client

        user1 = User(username="user1", email="user1@example.com")
        user1.set_password("pass1")
        user2 = User(username="user2", email="user2@example.com")
        user2.set_password("pass2")

        db.session.add_all([user1, user2])
        db.session.commit()

        self.user1 = user1
        self.user2 = user2

        self.user1_token = create_access_token(identity=str(user1.id))
        self.user2_token = create_access_token(identity=str(user2.id))

    def test_register(self):
        user_input = {
            'username': 'new_user',
            'email': 'new_user@example.com',
            'password': 'new_pass'
        }

        response = make_request(
            self.client,
            "POST",
            "/api/users/",
            data=user_input
        )

        assert response.status_code == 201
        user_result = response.get_json()

        assert user_result['username'] == user_input['username']
        assert user_result['email'] == user_input['email']
        assert 'id' in user_result
        assert 'password' not in user_result

    def test_register_duplicate_username(self):
        user_input = {
            'username': 'user1',
            'email': 'new_user@example.com',
            'password': 'pass1'
        }

        response = make_request(
            self.client,
            "POST",
            "/api/users/",
            data=user_input
        )

        assert response.status_code == 409

    def test_register_duplicate_email(self):
        user_input = {
            'username': 'new_user',
            'email': 'user1@example.com',
            'password': 'pass1'
        }

        response = make_request(
            self.client,
            "POST",
            "/api/users/",
            data=user_input
        )

        assert response.status_code == 409

    def test_register_invalid_data(self):
        user_input = {
            'username': 'test_user',
            'email': 'test@example.com'
            # missing password
        }

        response = make_request(
            self.client,
            "POST",
            "/api/users/",
            data=user_input
        )

        assert response.status_code == 422

    def test_get(self):
        response = make_request(
            self.client,
            "GET",
            "/api/users/me",
            token=self.user1_token
        )

        assert response.status_code == 200
        user_result = response.get_json()

        assert user_result['id'] == self.user1.id
        assert user_result['username'] == self.user1.username
        assert user_result['email'] == self.user1.email
        assert 'password' not in user_result

    def test_get_unauthorized(self):
        response = make_request(
            self.client,
            "GET",
            "/api/users/me"
        )

        assert response.status_code == 401

    def test_update_username(self):
        update_input = {
            'username': 'updated_user'
        }

        response = make_request(
            self.client,
            "PUT",
            "/api/users/me",
            token=self.user1_token,
            data=update_input
        )

        assert response.status_code == 200
        user_result = response.get_json()

        assert user_result['username'] == 'updated_user'
        assert user_result['email'] == self.user1.email


    def test_update(self):
        update_input = {
            'username': 'new_username',
            'email': 'new_email@example.com',
            'password': 'new_pass'
        }

        response = make_request(
            self.client,
            "PUT",
            "/api/users/me",
            token=self.user1_token,
            data=update_input
        )

        assert response.status_code == 200
        user_result = response.get_json()

        assert user_result['username'] == update_input['username']
        assert user_result['email'] == update_input['email']
