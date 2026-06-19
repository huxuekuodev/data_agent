from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.middleware.auth_middleware import get_current_user_uuid
from app.api.shemas.query_schema import QuerySchema
from app.dependencies.services.query_service import query_service
from app.services.query_service import QueryService

query_router = APIRouter()


@query_router.post("/api/query")
async def query(
    query: QuerySchema,
    user_uuid: str = Depends(get_current_user_uuid),
    query_service: QueryService = Depends(query_service),
):
    """
    查询接口
    需要在请求头中携带 Authorization: Bearer {token}
    token 中必须包含 user_uuid 字段
    """
    return StreamingResponse(
        query_service.query(query.query, user_uuid), media_type="text/event-stream"
    )
