from datetime import timedelta, datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, field_serializer, computed_field

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
        """Converts user provided timedelta to minutes, as the duration is stored in db."""
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
        """Converts user provided timedelta to minutes, as the duration is stored in db."""
        if self.duration:
            return int(self.duration.total_seconds() / 60)


class TaskResponse(BaseModel):
    id: int
    priority_score: int
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
        """
        Convert duration in minutes as it is stored in db,
        to timedelta as the user expects.
        """
        if duration is None:
            return None
        return timedelta(minutes=duration)

class TasksListResponse(BaseModel):
    tasks: List[TaskResponse]
