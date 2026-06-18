from pydantic import BaseModel


class UserLoginSchema(BaseModel):
    username: str
    password: str


class getUserInfoSchema(BaseModel):
    user_id: int
