import jwt
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt import ExpiredSignatureError, InvalidTokenError

from app.api.config.jwt_config import JWT_ALGORITHM, JWT_SECRET

# HTTP Bearer 认证方案
security = HTTPBearer()


async def get_current_user_uuid(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """
    从请求头 Authorization 中解析 JWT token，获取 user_uuid

    Args:
        credentials: HTTP Bearer 认证凭证

    Returns:
        user_uuid: 用户唯一标识

    Raises:
        HTTPException: token 无效、过期或缺少 user_uuid
    """
    token = credentials.credentials

    try:
        # 解析 JWT token
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])

        # 检查是否包含 user_uuid
        user_uuid = payload.get("user_uuid")
        if not user_uuid:
            raise HTTPException(status_code=401, detail="Token 中缺少用户标识信息")

        return user_uuid

    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token 已过期，请重新登录")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="无效的 Token，请重新登录")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token 解析失败: {str(e)}")


async def verify_token_optional(request: Request) -> str | None:
    """
    可选的 token 验证，如果 token 存在则解析，否则返回 None

    Args:
        request: FastAPI 请求对象

    Returns:
        user_uuid 或 None
    """
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    token = auth_header.replace("Bearer ", "")

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload.get("user_uuid")
    except Exception:
        return None
