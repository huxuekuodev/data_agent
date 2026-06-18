from pymilvus import AsyncMilvusClient

from app.clients.milvus_client_manager import milvus_client_manager


async def get_milvus_client() -> AsyncMilvusClient:
    milvusClient: AsyncMilvusClient = await milvus_client_manager.get_client()
    return milvusClient
