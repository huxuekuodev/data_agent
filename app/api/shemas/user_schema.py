from datetime import datetime

from pydantic import BaseModel


class UserLoginSchema(BaseModel):
    username: str


class UserInfoSchema(BaseModel):
    user_id: int
    user_uuid: str
    username: str
    nickname: str | None = None
    email: str | None = None
    mobile: str | None = None
    avatar_url: str | None = None
    status: int
    user_type: int
    token_quota: int
    token_used: int
    last_login_at: datetime | None = None
    created_at: datetime


class UserLoginResponse(BaseModel):
    message: str
    token: str
    user_uuid: str
    username: str
