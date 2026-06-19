import uuid
from datetime import datetime, timedelta

import jwt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.config.jwt_config import JWT_ALGORITHM, JWT_EXPIRE_DAYS, JWT_SECRET
from app.api.middleware.auth_middleware import get_current_user_uuid
from app.api.shemas.user_schema import (
    UserInfoSchema,
    UserLoginResponse,
    UserLoginSchema,
)
from app.dependencies.infrastructure.db_session import get_data_agent_server_session
from app.models.chat_user import ChatUser

user_router = APIRouter()


@user_router.get("/api/user/info", response_model=UserInfoSchema)
async def getUserInfo(
    user_uuid: str = Depends(get_current_user_uuid),
    session: AsyncSession = Depends(get_data_agent_server_session),
):
    """
    查询用户信息接口
    需要从请求头中获取 Authorization token，解析出 user_uuid
    """
    # 从 token 中解析的 user_uuid 查询用户
    result = await session.execute(
        select(ChatUser).where(ChatUser.user_uuid == user_uuid)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return UserInfoSchema(
        user_id=user.id,
        user_uuid=user.user_uuid,
        username=user.username,
        nickname=user.nickname,
        email=user.email,
        mobile=user.mobile,
        avatar_url=user.avatar_url,
        status=user.status,
        user_type=user.user_type,
        token_quota=user.token_quota,
        token_used=user.token_used,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
    )


@user_router.post("/api/user/login", response_model=UserLoginResponse)
async def Login(
    login_schema: UserLoginSchema,
    session: AsyncSession = Depends(get_data_agent_server_session),
):
    """
    登录接口
    如果用户名不存在，自动注册新用户
    返回包含 uuid 的 JWT token
    """
    # 查询用户是否存在
    result = await session.execute(
        select(ChatUser).where(ChatUser.username == login_schema.username)
    )
    user = result.scalar_one_or_none()

    # 如果用户不存在，自动注册
    if not user:
        user = ChatUser(
            user_uuid=str(uuid.uuid4()),
            username=login_schema.username,
            nickname=login_schema.username,  # 默认昵称等于用户名
            status=1,  # 正常状态
            user_type=1,  # 普通用户
            token_quota=10000,  # 默认 Token 额度
            token_used=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(user)
        await session.flush()  # 获取自增 ID

    # 更新最后登录时间和 IP
    user.last_login_at = datetime.utcnow()
    user.updated_at = datetime.utcnow()

    # 生成 JWT token，包含 uuid 字段
    jwt_payload = {
        "user_uuid": user.user_uuid,
        "username": user.username,
        "user_id": user.id,
        "exp": datetime.utcnow() + timedelta(days=JWT_EXPIRE_DAYS),
    }
    jwt_token = jwt.encode(jwt_payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    await session.commit()

    return UserLoginResponse(
        message="登录成功",
        token=jwt_token,
        user_uuid=user.user_uuid,
        username=user.username,
    )
