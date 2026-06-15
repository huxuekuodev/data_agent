from pymilvus import AsyncMilvusClient

from app.clients.milvus_collections.base_collection import BaseCollection
from app.core.log import logger


class DataAgentColumnCollection(BaseCollection):
    name = "data-agent-column"

    async def load(self, client: AsyncMilvusClient):
        try:
            await client.load_collection(self.name)
            logger.info(f"✅ 集合 [{self.name}] 已加载至内存")
        except Exception as e:
            await self.create(client)
            await client.load_collection(self.name)
            logger.info(f"✅ 集合 [{self.name}] 已加载至内存")

    async def create(self, client: AsyncMilvusClient):
        await client.create_collection(collection_name=self.name)
        await client.wait_for_collection_ready(collection_name=self.name)
        logger.info(f"✅ 集合 [{self.name}] 已创建")
