from flask import abort
import sqlalchemy as sa

from .models import Rule, Condition
from .schemas import RuleCreateInput, RuleUpdateInput
from src.priority.api.users.models import User
from src.priority.extensions import db
from src.priority.errors import bad_request


class RuleService:
    """
    Handles all business logic and database interactions for Rules.
    Only allows for operations of objects related to a specific user,
    passed as a user_id argument to all methods.
    """

    def get_all(self, user_id: int):
        """Get all rules for user."""
        user = db.get_or_404(User, user_id)
        return user.rules

    def create(self, user_id: int, rule_data: RuleCreateInput):
        """Creates a new rule for the user."""
        rule = Rule(
            name=rule_data.name,
            boost=rule_data.boost,
            user_id=user_id
        )

        for condition_data in rule_data.conditions:
            condition = Condition(
                field=condition_data.field,
                operator=condition_data.operator,
                value=condition_data.value
            )
            condition.rule = rule

        db.session.add(rule)
        db.session.commit()

        return rule

    def get(self, user_id: int, rule_id: int):
        """
        Gets a rule by id for the user.
        Throws HTTPException if rule does not exist, or it belongs to another user.
        """
        rule = db.session.scalar(
            sa.Select(Rule).where(Rule.id == rule_id)
        )

        if rule is None:
            abort(404, description="Rule not found")

        if rule.user_id != user_id:
            abort(403, description="Rule belongs to another user")

        return rule

    def update(self, user_id: int, rule_id: int, rule_data: RuleUpdateInput):
        """Updates an existing rule. Conditions will be replaced if specified."""
        rule = self.get(user_id, rule_id)

        if rule is None:
            return bad_request('this rule does not exist')

        update_data = rule_data.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            if key == "conditions":
                rule.conditions.clear()
                for condition_data in value:
                    condition = Condition(
                        field=condition_data['field'],
                        operator=condition_data['operator'],
                        value=condition_data['value']
                    )
                    condition.rule = rule
            else:
                setattr(rule, key, value)

        db.session.add(rule)
        db.session.commit()

        return rule

    def delete(self, user_id, rule_id: int):
        """Deletes a rule for the user."""
        rule = self.get(user_id, rule_id)

        db.session.delete(rule)
        db.session.commit()
