from datetime import timedelta, datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, ConfigDict, Field

TASK_ORDER_BY = Literal['priority_score', 'created_at', 'deadline']

class TagResponse(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class CategoryResponse(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class TasksFilterParams(BaseModel):
    completed: Optional[bool] = False
    order_by: Optional[TASK_ORDER_BY] = 'priority_score'


class TaskCreateInput(BaseModel):
    title: str
    completed: Optional[bool] = False
    duration: Optional[timedelta] = None
    deadline: Optional[datetime] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = []


class TaskUpdateInput(BaseModel):
    title: str = None
    completed: Optional[bool] = False
    duration: Optional[timedelta] = None
    deadline: Optional[datetime] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = []


class TaskResponse(BaseModel):
    id: int
    priority_score: int
    title: str
    completed: bool
    duration: Optional[timedelta] = None
    deadline: Optional[datetime] = None
    category: Optional[CategoryResponse] = None
    tags: Optional[List[TagResponse]] = []
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TasksListResponse(BaseModel):
    tasks: List[TaskResponse]
