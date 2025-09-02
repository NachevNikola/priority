from flask import Blueprint

api = Blueprint("api", __name__, url_prefix="/api")

from ..core import PriorityCalculator, ConditionEvaluator
from .rules.service import RuleService
from .tasks.service import TaskService

condition_evaluator = ConditionEvaluator()
priority_calculator = PriorityCalculator(condition_evaluator)
rule_service = RuleService()
task_service = TaskService(priority_calculator)
