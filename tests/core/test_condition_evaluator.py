import pytest
from datetime import datetime, timezone, timedelta

from src.priority.core import ConditionEvaluator

class TestConditionEvaluator:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.evaluator = ConditionEvaluator()

    def test_category_equals_match(self):
        result = self.evaluator.evaluate('category', 'work', 'equals', 'work')
        assert result is True

    def test_category_equals_no_match(self):
        result = self.evaluator.evaluate('category', 'personal', 'equals', 'work')
        assert result is False

    def test_tag_equals_match(self):
        tag_names = ['urgent', 'important', 'work']
        result = self.evaluator.evaluate('tag', tag_names, 'equals', 'urgent')
        assert result is True

    def test_tag_equals_no_match(self):
        tag_names = ['urgent', 'important']
        result = self.evaluator.evaluate('tag', tag_names, 'equals', 'work')
        assert result is False

    def test_tag_equals_match_uppercase(self):
        tag_names = ['urgent', 'important']
        result = self.evaluator.evaluate('tag', tag_names, 'equals', 'URGENT')
        assert result is True

    def test_duration_less_than_true(self):
        duration = timedelta(hours=1)
        result = self.evaluator.evaluate('duration', duration, 'less_than', 'PT2H')
        assert result is True

    def test_duration_less_than_equal(self):
        duration = timedelta(hours=2)
        result = self.evaluator.evaluate('duration', duration, 'less_than', 'PT2H')
        assert result is True

    def test_duration_less_than_false(self):
        duration = timedelta(hours=3)
        result = self.evaluator.evaluate('duration', duration, 'less_than', 'PT2H')
        assert result is False

    def test_duration_greater_than_true(self):
        duration = timedelta(hours=3)
        result = self.evaluator.evaluate('duration', duration, 'greater_than', 'PT2H')
        assert result is True

    def test_duration_greater_than_false(self):
        duration = timedelta(hours=1)
        result = self.evaluator.evaluate('duration', duration, 'greater_than', 'PT2H')
        assert result is False

    def test_deadline_less_than_true(self):
        deadline = datetime.now(timezone.utc) + timedelta(hours=1)
        result = self.evaluator.evaluate('deadline', deadline, 'less_than', 'PT2H')
        assert result is True

    def test_deadline_less_than_false(self):
        deadline = datetime.now(timezone.utc) + timedelta(hours=3)
        result = self.evaluator.evaluate('deadline', deadline, 'less_than', 'PT2H')
        assert result is False

    def test_deadline_greater_than_true(self):
        deadline = datetime.now(timezone.utc) + timedelta(hours=3)
        result = self.evaluator.evaluate('deadline', deadline, 'greater_than', 'PT2H')
        assert result is True

    def test_deadline_greater_than_false(self):
        deadline = datetime.now(timezone.utc) + timedelta(hours=1)
        result = self.evaluator.evaluate('deadline', deadline, 'greater_than', 'PT2H')
        assert result is False

    def test_created_at_less_than_true(self):
        created_at = datetime.now(timezone.utc) - timedelta(hours=1)
        result = self.evaluator.evaluate('created_at', created_at, 'less_than', 'PT2H')
        assert result is True

    def test_created_at_less_than_false(self):
        created_at = datetime.now(timezone.utc) - timedelta(hours=3)
        result = self.evaluator.evaluate('created_at', created_at, 'less_than', 'PT2H')
        assert result is False

    def test_created_at_greater_than_true(self):
        created_at = datetime.now(timezone.utc) - timedelta(hours=3)
        result = self.evaluator.evaluate('created_at', created_at, 'greater_than', 'PT2H')
        assert result is True

    def test_created_at_greater_than_false(self):
        created_at = datetime.now(timezone.utc) - timedelta(hours=1)
        result = self.evaluator.evaluate('created_at', created_at, 'greater_than', 'PT2H')
        assert result is False

    def test_unsupported_field(self):
        result = self.evaluator.evaluate('unknown', 'value', 'equals', 'test')
        assert result is False

    def test_unsupported_operator(self):
        result = self.evaluator.evaluate('category', 'work', 'unknown', 'work')
        assert result is False
