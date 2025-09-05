import pytest
from flask_jwt_extended import create_refresh_token
from tests.test_utils import make_request
from src.priority.api.users.models import User


class TestAuthRoutes:

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

        self.user1_refresh_token = create_refresh_token(identity=str(user1.id))
        self.user2_refresh_token = create_refresh_token(identity=str(user2.id))

    def test_login(self):
        login_input = {
            'email': 'user1@example.com',
            'password': 'pass1'
        }

        response = make_request(
            self.client,
            "POST",
            "/api/auth/login",
            data=login_input
        )

        assert response.status_code == 200
        auth_result = response.get_json()

        assert 'access_token' in auth_result
        assert 'refresh_token' in auth_result
        assert 'access_token_expires_at' in auth_result
        assert 'refresh_token_expires_at' in auth_result

    def test_login_invalid_email(self):
        login_input = {
            'email': 'nonexistent@example.com',
            'password': 'pass1'
        }

        response = make_request(
            self.client,
            "POST",
            "/api/auth/login",
            data=login_input
        )

        assert response.status_code == 401

    def test_login_invalid_password(self):
        login_input = {
            'email': 'user1@example.com',
            'password': 'wrong_pass'
        }

        response = make_request(
            self.client,
            "POST",
            "/api/auth/login",
            data=login_input
        )

        assert response.status_code == 401

    def test_login_missing_data(self):
        login_input = {
            'email': 'user1@example.com'
            # missing password
        }

        response = make_request(
            self.client,
            "POST",
            "/api/auth/login",
            data=login_input
        )

        assert response.status_code == 422

    def test_refresh_token(self):
        response = make_request(
            self.client,
            "POST",
            "/api/auth/token/refresh",
            token=self.user1_refresh_token
        )

        assert response.status_code == 200
        auth_result = response.get_json()

        assert 'access_token' in auth_result
        assert 'refresh_token' in auth_result
        assert 'access_token_expires_at' in auth_result
        assert 'refresh_token_expires_at' in auth_result

    def test_refresh_token_unauthorized(self):
        response = make_request(
            self.client,
            "POST",
            "/api/auth/token/refresh"
        )

        assert response.status_code == 401
