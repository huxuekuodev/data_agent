from pydantic import BaseModel


class UserLoginSchema(BaseModel):
    username: str


class getUserInfoSchema(BaseModel):
    user_id: int
