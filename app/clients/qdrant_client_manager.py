from dataclasses import dataclass, field
from typing import Optional

# 1. 修正了 QdrantClient 的拼写
from qdrant_client import AsyncQdrantClient

from app.conf.app_config import QdrantConfig, app_config


@dataclass
class QdrantClientManager:
    config: QdrantConfig

    # 使用 init=False，明确告诉 dataclass：这个属性不由外部显式传入，仅供内部使用
    client: Optional[AsyncQdrantClient] = field(default=None, init=False)

    def __post_init__(self):
        # 2. 推荐直接传 host 和 port，比自己拼 url 字符串更安全、更不容易出错
        self.client = AsyncQdrantClient(
            host=self.config.host, port=self.config.port, check_compatibility=False
        )

        # 如果你的配置必须用 URL，建议加个安全判断，防止 http:// 重复：
        # url = f"http://{self.config.host}:{self.config.port}" if not self.config.host.startswith("http") else f"{self.config.host}:{self.config.port}"
        # self.client = QdrantClient(url=url)

    async def close(self):
        if self.client:
            await self.client.close_async()


# 模块级单例，其他文件直接：from app.xxx import qdrant_client_manager 使用即可
qdrant_client_manager = QdrantClientManager(config=app_config.qdrant)


if __name__ == "__main__":
    import asyncio

    async def run():
        from qdrant_client.models import Distance, VectorParams

        qcm = QdrantClientManager(app_config.qdrant)
        await qcm.client.create_collection(
            collection_name="items",
            vectors_config=VectorParams(size=384, distance=Distance.COSINE),
        )

    asyncio.run(run())
