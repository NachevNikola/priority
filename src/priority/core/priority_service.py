from datetime import datetime, timezone, timedelta
from typing import Dict, Tuple, Callable, Any, List

from src.priority.api.tasks.models import Task
from src.priority.api.rules.models import Rule, Condition
from src.priority.utils import parse_timedelta


class ConditionEvaluator:
    """
    Evaluates field values against conditions.
    The class calls specific evaluation functions based on the field name and operator.
    It contains the implementation for all supported comparisons.
    """

    def __init__(self):
        self._evaluators_map: Dict[Tuple[str, str], Callable[[Any, str], bool]] = {
            ('category', 'equals'): self._category_equals,
            ('tag', 'equals'): self._tag_equals,
            ('duration', 'less_than'): self._duration_less_than,
            ('duration', 'greater_than'): self._duration_greater_than,
            ('deadline', 'less_than'): self._deadline_less_than,
            ('deadline', 'greater_than'): self._deadline_greater_than,
            ('created_at', 'less_than'): self._created_at_less_than,
            ('created_at', 'greater_than'): self._created_at_greater_than,
        }

    def evaluate(self, field_name: str, field_value: Any, operator: str, condition_value: str) -> bool:
        """
        Calls the specific evaluation function based on the field name and operator
        which will compare the field and condition values
        """
        evaluator_function = self._evaluators_map.get((field_name, operator))

        if evaluator_function is None:
            return False

        return evaluator_function(field_value, condition_value)

    def _category_equals(self, category_name: str, value: str) -> bool:
        """Checks if the category matches"""
        return category_name == value.lower()

    def _tag_equals(self, tag_names: List[str], value: str) -> bool:
        """Checks if a tag exists in a list of tag names"""
        return value.lower() in tag_names

    def _duration_less_than(self, duration: timedelta, value: str) -> bool:
        """Checks if the duration in minutes is less than  or equals to the given timedelta"""
        value_timedelta = parse_timedelta(value)
        return duration <= value_timedelta

    def _duration_greater_than(self, duration: timedelta, value: str) -> bool:
        """Checks if the duration in minutes is greater than the given timedelta"""
        value_timedelta = parse_timedelta(value)
        return duration > value_timedelta

    def _deadline_less_than(self, deadline: datetime, value: str) -> bool:
        """Checks if the deadline is within the timedelta from now."""
        value_timedelta = parse_timedelta(value)
        return deadline <= (datetime.now(timezone.utc) + value_timedelta)

    def _deadline_greater_than(self, deadline: datetime, value: str) -> bool:
        """Checks if the deadline is later than the timedelta from now."""
        value_timedelta = parse_timedelta(value)
        return deadline > (datetime.now(timezone.utc) + value_timedelta)

    def _created_at_greater_than(self, created_at: datetime, value: str) -> bool:
        """Checks if created_at is more timedelta from now in the past"""
        value_timedelta = parse_timedelta(value)
        return created_at <= (datetime.now(timezone.utc) - value_timedelta)

    def _created_at_less_than(self, created_at: datetime, value: str) -> bool:
        """Checks if created_at is within timedelta from now in the past"""
        value_timedelta = parse_timedelta(value)
        return created_at > (datetime.now(timezone.utc) - value_timedelta)


class PriorityCalculator:
    """Calculates the task's priority score based on user's rules."""

    def __init__(self, condition_evaluator: ConditionEvaluator):
        self.condition_evaluator = condition_evaluator

    def calculate_task_score(self, task: Task) -> int:
        """
        Calculates the task priority score by iterating the user's rules
        and adding the boost of the rules that apply
        """
        if not task.user:
            return 0

        total_score = 0

        for rule in task.user.rules:
            if self._rule_applies(task, rule):
                total_score += rule.boost
        return total_score

    def _rule_applies(self, task: Task, rule: Rule) -> bool:
        """Checks if all the conditions for a given rule apply"""
        if not rule.conditions:
            return False
        return all(self._condition_applies(task, condition) for condition in rule.conditions)

    def _condition_applies(self, task: Task, condition: Condition) -> bool:
        """
        Checks if a specific condition applies to the given task.
        Extracts the task field information and calls ConditionEvaluator.
        """
        field_value_map = {
            'category': task.category.name if task.category else None,
            'tag': [tag.name for tag in task.tags],
            'duration': task.duration,
            'deadline': task.deadline,
            'created_at': task.created_at,
        }

        field_value = field_value_map.get(condition.field, None)
        if field_value is None:
            return False

        return self.condition_evaluator.evaluate(
            field_name=condition.field,
            field_value=field_value,
            operator=condition.operator,
            condition_value=condition.value
        )
