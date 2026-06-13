from dataclasses import dataclass

from elasticsearch import AsyncElasticsearch
from pydantic import Field

from app.conf.app_config import ESConfig, app_config


@dataclass
class ESClientManager:
    config: ESConfig
    client: AsyncElasticsearch = Field(default=None, init=False)

    def __post_init__(self):
        self.client = AsyncElasticsearch(
            hosts=[f"http://{self.config.host}:{self.config.port}"],
        )

    async def close(self):
        if self.client:
            await self.client.aclose()


es_client_manager = ESClientManager(config=app_config.es)

# 测试
if __name__ == "__main__":
    import asyncio

    async def test():
        await es_client_manager.client.indices.create(index="items")

        await es_client_manager.close()

    asyncio.run(test())
