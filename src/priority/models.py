from datetime import datetime, timezone
from typing import Optional, List
import sqlalchemy as sa
import sqlalchemy.orm as so
from src.priority.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

task_tags = sa.Table(
    'task_tags',
    db.metadata,
    sa.Column('task_id', sa.Integer, sa.ForeignKey('task.id'),
              primary_key=True),
    sa.Column('tag_id', sa.Integer, sa.ForeignKey('tag.id'),
              primary_key=True)
)

class User(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    tasks: so.Mapped[List['Task']] = so.relationship(back_populates='user', cascade='all, delete-orphan')
    categories: so.Mapped[List['Category']] = so.relationship(back_populates='user', cascade='all, delete-orphan')
    tags: so.Mapped[List['Tag']] = so.relationship(back_populates='user', cascade='all, delete-orphan')
    rules: so.Mapped[List['Rule']] = so.relationship(back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
        }
        return data

    def from_dict(self, data, new_user=False):
        for field in ['username', 'email', 'about_me']:
            if field in data:
                setattr(self, field, data[field])
        if new_user and 'password' in data:
            self.set_password(data['password'])


class Task(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(140))
    completed: so.Mapped[bool] = so.mapped_column(default=False)
    duration: so.Mapped[Optional[int]] = so.mapped_column()
    deadline: so.Mapped[Optional[datetime]] = so.mapped_column(sa.DateTime(timezone=True), index=True)
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.DateTime(timezone=True), index=True, default=lambda: datetime.now(timezone.utc)
    )

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    user: so.Mapped[User] = so.relationship(back_populates='tasks')
    category_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey('category.id'))
    category: so.Mapped[Optional['Category']] = so.relationship(back_populates='tasks')

    tags: so.Mapped[List['Tag']] = so.relationship(secondary=task_tags, back_populates='tasks')

    def __repr__(self):
        return f'<Task {self.title}>'


class Category(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(50))

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    user: so.Mapped[User] = so.relationship(back_populates='categories')

    tasks: so.Mapped[List[Task]] = so.relationship(back_populates='category')

    def __repr__(self):
        return f'<Category {self.name}>'

class Tag(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(50))

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    user: so.Mapped[User] = so.relationship(back_populates='tags')

    tasks: so.Mapped[List['Task']] = so.relationship(secondary=task_tags, back_populates='tags')

    def __repr__(self):
        return f'<Tag {self.name}>'

class Rule(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(100))
    boost: so.Mapped[int] = so.mapped_column(default=0)

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    user: so.Mapped[User] = so.relationship(back_populates='rules')

    conditions: so.Mapped[List['Condition']] = so.relationship(back_populates='rule', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Rule {self.name}>'

class Condition(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    field: so.Mapped[str] = so.mapped_column(sa.String(50))
    operator: so.Mapped[str] = so.mapped_column(sa.String(50))
    value: so.Mapped[str] = so.mapped_column(sa.String(255))

    rule_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Rule.id), index=True)
    rule: so.Mapped[Rule] = so.relationship(back_populates='conditions')

    def __repr__(self):
        return f'<Condition: {self.field} {self.operator} {self.value}>'
