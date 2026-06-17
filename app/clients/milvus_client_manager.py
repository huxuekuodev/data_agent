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

    # async def init_collections(self):
    #     """
    #     项目启动时调用的统一初始化和加载入口
    #     """
    #     # 1. 确保 client 已经由于当前事件循环被成功建立
    #     client = await self.get_client()
        
    #     # 2. 实例化你的各个具体集合类，并传入安全的 client
    #     collections_to_load = [
    #         DataAgentColumnCollection(client),
    #         # UserCollection(client),  # 举例：其他需要初始化的集合
    #     ]
        
    #     # 3. 循环异步执行各个集合自身的加载/创建幂等逻辑
    #     for col in collections_to_load:
    #         try:
    #             await col.load()
    #         except Exception as e:
    #             logger.error(f"❌ 初始化 Milvus 集合 [{col.name}] 失败: {e}")
    #             raise e

    async def close(self):
        if self.client is not None:
            await self.client.close()
            self.client = None


milvus_client_manager = MilvusClientManager(config=app_config.milvus)
