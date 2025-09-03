from pydantic import BaseModel

class LoginInput(BaseModel):
    email: str
    password: str

    class Config:
        json_schema_extra = {
            'example': {
                'email': 'user1@example.com',
                'password': 'user1_password',
            }
        }

class AccessTokensResponse(BaseModel):
    access_token: str
    access_token_expires_at: str
    refresh_token: str
    refresh_token_expires_at: str
