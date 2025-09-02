from datetime import datetime

from pydantic import BaseModel

class LoginInput(BaseModel):
    email: str
    password: str

class AccessTokensResponse(BaseModel):
    access_token: str
    access_token_expires_at: str
    refresh_token: str
    refresh_token_expires_at: str
