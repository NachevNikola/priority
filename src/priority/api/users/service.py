from typing import Optional

from flask import abort
import sqlalchemy as sa

from src.priority.extensions import db
from .models import User

from .schemas import UserCreateInput, UserUpdateInput

class UserService:
    """
    Handles all business logic and database operations for Users.
    """
    def register(self, user_data: UserCreateInput):
        """
        Register a new user if the username and email are available.
        """
        self._check_available_username(user_data.username)
        self._check_available_email(user_data.email)

        user = User(
            username=user_data.username,
            email=user_data.email,
        )
        user.set_password(user_data.password)
        db.session.add(user)
        db.session.commit()

        return user

    def get(self, user_id: int):
        """Get a user by id"""
        user = db.session.scalar(sa.select(User).where(User.id == user_id))
        if user is None:
            abort(404, description='User not found')

        return user

    def update(self, user_id: int, user_data: UserUpdateInput):
        """Update a user if the username and email values are available"""
        user = self.get(user_id)

        update_data = user_data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            if key == 'username':
                self._check_available_username(value, user.username)
            if key == 'email':
                self._check_available_email(value, user.email)
            if key == 'password':
                user.set_password(value)
            else:
                setattr(user, key, value)

        db.session.add(user)
        db.session.commit()

        return user

    def _check_available_username(self, new_username: str, current_username: Optional[str] = None):
        """Check if the specified new username doesn't exist in db or is equal to the current username"""
        if current_username == new_username:
            return

        duplicate_user =  db.session.scalar(sa.select(User).where(User.username == new_username))

        if duplicate_user is not None:
            abort(409, description='Username already exists')

    def _check_available_email(self, new_email: str, current_email: Optional[str] = None):
        """Check if the specified new email doesn't exist in db or is equal to the current email"""
        if current_email == new_email:
            return

        duplicate_user = db.session.scalar(sa.select(User).where(User.email == new_email))

        if duplicate_user is not None:
            abort(409, description='Email already exists')
