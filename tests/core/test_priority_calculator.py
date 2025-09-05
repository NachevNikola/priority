import pytest
from unittest.mock import Mock

from src.priority.core import PriorityCalculator

class TestPriorityCalculator:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.condition_evaluator = Mock()
        self.calculator = PriorityCalculator(self.condition_evaluator)

    def test_calculate_task_score_no_user(self):
        task = Mock()
        task.user = None

        score = self.calculator.calculate_task_score(task)
        assert score == 0

    def test_calculate_task_score_no_rules(self):
        user = Mock()
        user.rules = []
        task = Mock()
        task.user = user

        score = self.calculator.calculate_task_score(task)
        assert score == 0

    def test_calculate_task_score_rules_apply(self):
        rule1 = Mock()
        rule1.boost = 10
        rule1.conditions = [Mock()]

        rule2 = Mock()
        rule2.boost = 5
        rule2.conditions = [Mock()]

        user = Mock()
        user.rules = [rule1, rule2]

        task = Mock()
        task.user = user

        # Mock _rule_applies to return True for both rules
        self.calculator._rule_applies = Mock(return_value=True)

        score = self.calculator.calculate_task_score(task)
        assert score == 15

    def test_rule_applies_no_conditions(self):
        rule = Mock()
        rule.conditions = []
        task = Mock()

        result = self.calculator._rule_applies(task, rule)
        assert result is False

    def test_rule_applies_all_conditions_match(self):
        condition1 = Mock()
        condition2 = Mock()
        rule = Mock()
        rule.conditions = [condition1, condition2]
        task = Mock()

        self.calculator._condition_applies = Mock(return_value=True)

        result = self.calculator._rule_applies(task, rule)
        assert result is True

    def test_rule_applies_some_conditions_fail(self):
        condition1 = Mock()
        condition2 = Mock()
        rule = Mock()
        rule.conditions = [condition1, condition2]
        task = Mock()

        self.calculator._condition_applies = Mock(side_effect=[True, False])

        result = self.calculator._rule_applies(task, rule)
        assert result is False
