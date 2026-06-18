from datetime import datetime, timedelta

import jwt
from fastapi import APIRouter

from app.api.shemas.user_schema import UserLoginSchema

user_router = APIRouter()


@user_router.get("/user/info")
async def getUserInfo():
    # 从数据库获取用户信息
    user_id = 1
    return {"user_id": user_id}


@user_router.post("/user/login")
async def Login(login_schema: UserLoginSchema):
    # 登录逻辑
    jwt_token = jwt.encode(
        {
            "username": login_schema.username,
            "exp": datetime.now() + timedelta(days=15),
        },
        "secret",
        algorithm="HS256",
    )
    return {"message": "登录成功", "token": jwt_token}
