import asyncio
import logging
from dataclasses import dataclass
from typing import Optional



# 导入原生的异步客户端、数据类型和索引/查询构造器
from pymilvus import (
    AsyncMilvusClient,
)

from app.clients.embedding_client import OllamaEmbedding
from app.conf.app_config import MilvusConfig, app_config

logger = logging.getLogger(__name__)


class MilvusClientManager:
    def __init__(self, config: MilvusConfig):
        self.config = config
        self.collection_name = config.collection_name
        # 1. 延迟初始化原生的异步客户端，避免事件循环问题
        self.uri = f"http://{config.host}:{config.port}"
        self.client: Optional[AsyncMilvusClient] = None
        
    async def get_client(self) -> AsyncMilvusClient:
        if self.client is None:
            self.client = AsyncMilvusClient(uri=self.uri, token=self.config.token)
        return self.client

    async def close(self):
        if self.client is not None:
            await self.client.close()
            self.client = None


milvus_client_manager = MilvusClientManager(config=app_config.milvus)
