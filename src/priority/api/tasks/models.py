from datetime import datetime, timezone
from typing import Optional, List
import sqlalchemy as sa
import sqlalchemy.orm as so
from src.priority.extensions import db
from src.priority.api.users.models import User


task_tags = sa.Table(
    'task_tags',
    db.metadata,
    sa.Column('task_id', sa.Integer, sa.ForeignKey('task.id'),
              primary_key=True),
    sa.Column('tag_id', sa.Integer, sa.ForeignKey('tag.id'),
              primary_key=True)
)


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
