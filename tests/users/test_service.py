import pytest
from werkzeug.exceptions import Conflict

from tests.conftest import db
import sqlalchemy as sa
from src.priority.api.users.models import User
from src.priority.api.users.schemas import UserCreateInput, UserUpdateInput
from src.priority.api.users.service import UserService


def test_register(db):
    user_input = UserCreateInput(
        username="user1",
        email="user1@example.com",
        password="user1"
    )

    UserService().register(user_input)
    user = db.session.scalar(sa.Select(User))
    assert user.username == user_input.username
    assert user.email == user_input.email
    assert user.check_password(user_input.password)

def test_get(db):
    user1 = User(id=1, username="user1", email="user1@example.com")
    db.session.add(user1)
    db.session.commit()

    user_response = UserService().get(user1.id)
    assert user_response.username == user1.username
    assert user_response.email == user1.email

def test_update(db):
    user1 = User(id=1, username="user1", email="user1@example.com")
    db.session.add(user1)
    db.session.commit()

    update_input = UserUpdateInput(username="user2", email="user2@example.com")
    UserService().update(user1.id, update_input)

    user = db.session.scalar(sa.Select(User))
    assert user.username == update_input.username
    assert user.email == update_input.email

def test_check_available_username(db):
    user1 = User(id=1, username="user1", email="user1@example.com")
    db.session.add(user1)
    db.session.commit()

    assert UserService()._check_available_username("user2")


def test_check_available_username_duplicate(db):
    user1 = User(id=1, username="user1", email="user1@example.com")
    db.session.add(user1)
    db.session.commit()

    with pytest.raises(Conflict):
        UserService()._check_available_username(user1.username)


def test_check_available_email(db):
    user1 = User(id=1, username="user1", email="user1@example.com")
    db.session.add(user1)
    db.session.commit()

    assert UserService()._check_available_email("user2@example.com")

def test_check_available_email_duplicate(db):
    user1 = User(id=1, username="user1", email="user1@example.com")
    db.session.add(user1)
    db.session.commit()

    with pytest.raises(Conflict):
        UserService()._check_available_email("user1@example.com")
