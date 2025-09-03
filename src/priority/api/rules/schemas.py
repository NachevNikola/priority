from typing import List, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict, model_validator
from src.priority.utils import parse_timedelta

ALLOWED_FIELDS = Literal["category", "tag", "duration", "deadline", "created_at"]
ALLOWED_OPERATORS = Literal["equals", "greater_than", "less_than"]
FIELDS_REQUIRING_TIMEDELTA_VALUE = ("duration", "deadline", "created_at")


class ConditionCreateInput(BaseModel):
    field: ALLOWED_FIELDS
    operator: ALLOWED_OPERATORS
    value: str

    @model_validator(mode='after')
    def validate_value_for_field(self):
        """Validate that the condition value has a compatible type with the task field"""
        if self.field in FIELDS_REQUIRING_TIMEDELTA_VALUE:
            parse_timedelta(self.value)
        return self

class ConditionResponse(BaseModel):
    id: int
    field: str
    operator: str
    value: str

    model_config = ConfigDict(from_attributes=True)


class RuleCreateInput(BaseModel):
    name: str
    boost: int
    conditions: List[ConditionCreateInput] = Field(..., min_length=1)

    class Config:
        json_schema_extra = {
            'example': {
                'name': 'Rule for urgent work tasks with close deadline that were recently created',
                'boost': 30,
                'conditions': [
                    {
                        'field' : 'category',
                        'operator' : 'equals',
                        'value' : 'work',
                    },
                    {
                        'field': 'tag',
                        'operator': 'equals',
                        'value': 'urgent',
                    },
                    {
                        'field': 'deadline',
                        'operator': 'less_than',
                        'value': 'P7DT12H'
                    },
                    {
                        'field': 'duration',
                        'operator': 'greater_than',
                        'value': 'PT30M'
                    },
                    {
                        'field': 'created_at',
                        'operator': 'less_than',
                        'value': 'P14D'
                    }
                ]
            }
        }


class RuleUpdateInput(BaseModel):
    name: Optional[str] = None
    boost: Optional[int] = None
    conditions: Optional[List[ConditionCreateInput]] = Field(None, min_length=1)


class RuleResponse(BaseModel):
    id: int
    name: str
    boost: int
    conditions: List[ConditionResponse]

    model_config = ConfigDict(from_attributes=True)


class RulesListResponse(BaseModel):
    rules: List[RuleResponse]
