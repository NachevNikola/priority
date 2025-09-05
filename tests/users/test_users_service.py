import pytest
from werkzeug.exceptions import Conflict

import sqlalchemy as sa
from src.priority.api.users.models import User
from src.priority.api.users.schemas import UserCreateInput, UserUpdateInput
from src.priority.api.users.service import UserService

class TestUserService:
    @pytest.fixture(autouse=True)
    def setup(self, db):
        self.db = db
        self.service = UserService()

        user1 = User(username="user1", email="user1@example.com")
        db.session.add(user1)
        db.session.commit()

        self.user1 = user1

    def test_register(self, db):
        user_input = UserCreateInput(
            username="new_user",
            email="new_usere@example.com",
            password="new_user"
        )

        UserService().register(user_input)
        user = db.session.scalar(sa.Select(User).where(
            User.username == user_input.username)
        )
        assert user.email == user_input.email
        assert user.check_password(user_input.password)

    def test_get(self):
        user_response = UserService().get(self.user1.id)
        assert user_response.username == self.user1.username
        assert user_response.email == self.user1.email

    def test_update(self, db):
        update_input = UserUpdateInput(username="user2", email="user2@example.com")
        UserService().update(self.user1.id, update_input)

        user = db.session.scalar(sa.Select(User))
        assert user.username == update_input.username
        assert user.email == update_input.email

    def test_check_available_username(self):
        assert UserService()._check_available_username("user2")

    def test_check_available_username_duplicate(self):
        with pytest.raises(Conflict):
            UserService()._check_available_username(self.user1.username)

    def test_check_available_email(self):
        assert UserService()._check_available_email("user2@example.com")

    def test_check_available_email_duplicate(self):
        with pytest.raises(Conflict):
            UserService()._check_available_email("user1@example.com")
