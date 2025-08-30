from typing import List, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict

ALLOWED_FIELDS = Literal["category", "tags", "deadline"]
ALLOWED_OPERATORS = Literal["equals", "greater_than", "less_than"]


class ConditionCreateModel(BaseModel):
    field: ALLOWED_FIELDS
    operator: ALLOWED_OPERATORS
    value: str


class ConditionResponse(BaseModel):
    id: int
    field: str
    operator: str
    value: str

    model_config = ConfigDict(from_attributes=True)


class RuleCreateModel(BaseModel):
    name: str
    boost: int
    conditions: List[ConditionCreateModel] = Field(..., min_length=1)


class RuleUpdateModel(BaseModel):
    name: Optional[str] = None
    boost: Optional[int] = None
    conditions: Optional[List[ConditionCreateModel]] = Field(None, min_length=1)


class RuleResponse(BaseModel):
    id: int
    name: str
    boost: int
    conditions: List[ConditionResponse]

    model_config = ConfigDict(from_attributes=True)


class RulesListResponse(BaseModel):
    rules: List[RuleResponse]

