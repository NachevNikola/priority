from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserCreateInput(BaseModel):
    username: str
    email: str
    password: str

class UserUpdateInput(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    model_config = ConfigDict(from_attributes=True)
