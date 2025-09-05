import pytest
from werkzeug.exceptions import NotFound, Forbidden

from src.priority.api.rules.models import Rule, Condition
from src.priority.api.rules.schemas import ConditionCreateInput, RuleCreateInput, RuleUpdateInput
from src.priority.api.rules.service import RuleService
from src.priority.api.users.models import User


class TestRulesService:

    @pytest.fixture(autouse=True)
    def setup(self, db):
        user1 = User(username="user1", email="user1@example.com")
        user2 = User(username="user2", email="user2@example.com")

        condition1 = Condition(field="category", operator="equals", value="work")
        condition2 = Condition(field="tag", operator="equals", value="priority")
        rule1 = Rule(name="rule1", boost=5, user_id=1, conditions=[condition1])
        rule2 = Rule(name="rule2", boost=10, user_id=1, conditions=[condition1, condition2])
        rule3 = Rule(name="rule3", boost=15, user_id=2, conditions=[condition2])

        db.session.add_all([user1, user2, condition1, condition2, rule1, rule2])
        db.session.commit()

        self.user1 = user1
        self.rule1 = rule1
        self.rule2 = rule2
        self.rule3 = rule3
        self.service = RuleService()


    def test_get_all(self,):
        rules = self.service.get_all(self.user1.id)
        assert len(rules) == 2
        assert self.rule1 in rules
        assert self.rule2 in rules
        assert self.rule3 not in rules

    def test_get_all_nonexistent_user(self):
        with pytest.raises(NotFound):
            self.service.get_all(999)

    def test_create_rule_with_conditions(self):
        """Test creating a new rule with conditions."""
        condition_data1 = ConditionCreateInput(field="duration", operator="greater_than", value="PT30M")
        condition_data2 = ConditionCreateInput(field="category", operator="equals", value="work")
        rule_data = RuleCreateInput(
            name="test rule",
            boost=15,
            conditions=[condition_data1, condition_data2]
        )

        rule = self.service.create(self.user1.id, rule_data)

        assert rule.name == rule_data.name
        assert rule.boost == rule_data.boost
        assert rule.user_id == self.user1.id
        assert len(rule.conditions) == 2
        condition1 = rule.conditions[0]
        assert condition1.field == condition_data1.field
        assert condition1.operator == condition_data1.operator
        assert condition1.value == condition_data1.value

        condition2 = rule.conditions[1]
        assert condition2.field == condition_data2.field
        assert condition2.operator == condition_data2.operator
        assert condition2.value == condition_data2.value

    def test_get_existing_rule_same_user(self):
        rule = self.service.get(self.user1.id, self.rule1.id)

        assert rule == self.rule1
        assert rule.name == "rule1"

    def test_get_nonexistent_rule_raises_404(self):
        with pytest.raises(NotFound) as exc_info:
            self.service.get(self.user1.id, 999)

        assert "Rule not found" in str(exc_info.value.description)

    def test_get_rule_different_user_raises_403(self):
        with pytest.raises(Forbidden) as exc_info:
            self.service.get(self.user1.id, self.rule3.id)

        assert "Rule belongs to another user" in str(exc_info.value.description)

    def test_update_rule(self):
        condition_data = ConditionCreateInput(field="deadline", operator="less_than", value="PT6H")
        rule_data = RuleUpdateInput(
            name="updated rule",
            boost=20,
            conditions=[condition_data]
        )

        updated_rule = self.service.update(self.user1.id, self.rule2.id, rule_data)

        assert len(updated_rule.conditions) == 1
        assert updated_rule.name == rule_data.name
        assert updated_rule.boost == rule_data.boost
        assert updated_rule.conditions[0].field == condition_data.field
        assert updated_rule.conditions[0].operator == condition_data.operator

    def test_delete_existing_rule(self):
        self.service.delete(self.user1.id, self.rule1.id)

        # Verify rule is deleted
        with pytest.raises(NotFound):
            self.service.get(self.user1.id, self.rule1.id)
