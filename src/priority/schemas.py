from datetime import timedelta, datetime
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict, field_serializer, computed_field

ALLOWED_FIELDS = Literal["category", "tags", "deadline"]
ALLOWED_OPERATORS = Literal["equals", "greater_than", "less_than"]


class ConditionCreateInput(BaseModel):
    field: ALLOWED_FIELDS
    operator: ALLOWED_OPERATORS
    value: str


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


class TagResponse(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class CategoryResponse(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class TaskCreateInput(BaseModel):
    title: str
    completed: Optional[bool] = False
    duration: Optional[timedelta] = None
    deadline: Optional[datetime] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = []

    @computed_field()
    @property
    def duration_minutes(self) -> Optional[int]:
        if self.duration:
            return int(self.duration.total_seconds() / 60)


class TaskUpdateInput(BaseModel):
    title: str = None
    completed: Optional[bool] = False
    duration: Optional[timedelta] = None
    deadline: Optional[datetime] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = []

    @computed_field()
    @property
    def duration_minutes(self) -> Optional[int]:
        if self.duration:
            return int(self.duration.total_seconds() / 60)


class TaskResponse(BaseModel):
    id: int
    title: str
    completed: bool
    duration: Optional[int] = None
    deadline: Optional[datetime] = None
    category: Optional[CategoryResponse] = None
    tags: Optional[List[TagResponse]] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('duration')
    def serialize_duration_minutes_to_timedelta(self, duration: Optional[int]) -> Optional[timedelta]:
        if duration is None:
            return None
        return timedelta(minutes=duration)

class TasksListResponse(BaseModel):
    tasks: List[TaskResponse]
