from pymilvus import AsyncMilvusClient
from pymilvus.exceptions import MilvusException, DescribeCollectionException


class BaseCollection:
    name = ""
    def __init__(self, client:AsyncMilvusClient):
        self.client = client

    # 检查集合是否存在
    async def has_collection(self):
        try:
            # 使用 AsyncGrpcHandler 提供的 describe_collection
            await self.client._get_connection().describe_collection(collection_name=self.name)
            return True
        except DescribeCollectionException:
            # 明确是集合不存在
            return False
        except MilvusException as e:
            # 其他 Milvus 异常（如权限问题等），我们抛出
            raise e
        except Exception as e:
            # 其他异常（如网络问题），我们抛出
            raise e

    @abstractmethod
    async def load(self, client: AsyncMilvusClient):
        pass
