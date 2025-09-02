from typing import List
import sqlalchemy as sa
import sqlalchemy.orm as so
from src.priority.extensions import db
from src.priority.api.users.models import User

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
