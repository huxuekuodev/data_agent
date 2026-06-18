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
    return {"message": "登录成功"}
