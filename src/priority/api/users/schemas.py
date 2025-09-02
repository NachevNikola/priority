from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserCreateInput(BaseModel):
    username: str
    email: str
    password: str

class UserUpdateInput(BaseModel):
    username: Optional[str]
    email: Optional[str]
    password: Optional[str]

class UserResponse(BaseModel):
    id: int
    username: str
    email: str

    model_config = ConfigDict(from_attributes=True)
