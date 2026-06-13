import asyncio
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

# 导入原生的异步客户端、数据类型和索引/查询构造器
from pymilvus import AsyncMilvusClient, DataType, Function, FunctionType

from app.clients.embedding_client import OllamaEmbedding
from app.conf.app_config import MilvusConfig, app_config

logger = logging.getLogger(__name__)


class MilvusClientManager:
    def __init__(self, config: MilvusConfig):
        self.config = config
        self.collection_name = config.collection_name

        # 1. 初始化原生的异步客户端
        uri = f"http://{config.host}:{config.port}"
        self.client = AsyncMilvusClient(uri=uri, token=config.token)

    async def init_collection_and_index(self, drop_old: bool = True):
        """
        异步初始化：支持双索引（HNSW + 稀疏倒排）、内置 BM25 函数以及开启动态字段
        """
        try:
            await self.client.drop_collection(self.collection_name)
            logger.info(f"📡 正在异步创建双索引混合检索集合: {self.collection_name}...")
            # 【配置核心一】创建 Schema，并明确开启 enable_dynamic_field=True（自动支持任意 metadata）
            schema = self.client.create_schema(enable_dynamic_field=True)
            # 定义显式字段
            schema.add_field(
                field_name="id",
                datatype=DataType.INT64,
                is_primary=True,
                auto_id=True,
            )
            schema.add_field(
                field_name="text",
                datatype=DataType.VARCHAR,
                max_length=65535,
                enable_analyzer=True,
                analyzer_params={"tokenizer": "jieba"},
            )  # 必须显式定义文本字段，供 BM25 分词
            schema.add_field(
                field_name="vector",
                datatype=DataType.FLOAT_VECTOR,
                dim=self.config.embedding_size,
            )
            schema.add_field(
                field_name="sparse",
                datatype=DataType.SPARSE_FLOAT_VECTOR,
            )  # 稀疏向量字段，存储分词权重

            # 【配置核心二】配置原生的 BM25 内置分词函数 (替代 LangChain 的 BM25BuiltInFunction)
            bm25_function = Function(
                name="text_bm25_emb",
                function_type=FunctionType.BM25,  # 使用内置 BM25 文本转稀疏向量功能
                input_field_names=["text"],
                output_field_names=["sparse"],
            )
            schema.add_function(bm25_function)

            # 创建集合
            await self.client.create_collection(
                collection_name=self.collection_name, schema=schema
            )
            # 【配置核心三】异步为稠密向量和稀疏向量分别建立索引
            logger.info(f"⚙️ 正在创建生产级双索引（HNSW + 稀疏倒排）...")
            index_params = self.client.prepare_index_params()

            # 索引 1：稠密向量 HNSW (精确还原你指定的生产级参数)
            index_params.add_index(
                field_name="vector",
                index_name="vector_idx",
                index_type="HNSW",
                metric_type="COSINE",
                params={"M": 16, "efConstruction": 300},
            )

            # 索引 2：稀疏向量 倒排索引
            index_params.add_index(
                field_name="sparse",
                index_name="sparse_idx",
                index_type="SPARSE_INVERTED_INDEX",
                metric_type="BM25",  # 显式指定稀疏向量的 BM25 匹配度量
            )

            await self.client.create_index(
                collection_name=self.collection_name, index_params=index_params
            )

            # 异步加载集合至内存
            await self.client.load_collection(self.collection_name)
            logger.info(
                f"✅ Milvus 混合检索集合 [{self.collection_name}] 异步加载成功！"
            )

        except Exception as e:
            logger.error(f"❌ 异步初始化 Milvus 失败: {e}")
            raise e

    async def add_document_async(
        self, text: str, vector: List[float], metadata: Optional[Dict[str, Any]] = None
    ) -> List[Any]:
        """
        异步数据插入。依靠内置的 Function，你只需传入原始 text 和 dense 向量，
        Milvus 会自动调用内置的 jieba（取决于服务器端配置）计算出 sparse 向量。
        """
        if metadata is None:
            metadata = {}

        entity = {
            "text": text,
            "vector": vector,
            **metadata,  # metadata 作为动态字段平铺存入
        }

        res = await self.client.insert(
            collection_name=self.collection_name, data=[entity]
        )
        return res.get("ids", [])

    async def close(self):
        await self.client.close()


milvus_client_manager = MilvusClientManager(config=app_config.milvus)

# async def test_milvus_add_document():
#     # 1. 实例化 Ollama 嵌入模型
#     logger.info("🤖 正在初始化 OllamaEmbedding 模型...")
#     embed = OllamaEmbedding(embed_config=app_config.embedding)

#     # 2. 准备测试数据和对应的元数据（Metadata）
#     test_text = "人工智能和微服务架构正在深度融合，改变传统的软件开发模式。"

#     # 利用动态字段特性，塞入结构不固定的业务元数据
#     test_metadata = {
#         "user_id": "hu_dev_2026",
#         "project_name": "data_agent",
#         "category": "Architecture",
#         "level": "production",
#         "is_valid": True,
#     }

#     # 3. 将文本转化为 1024 维的稠密向量
#     logger.info("🔮 正在调用 Ollama 生成稠密向量...")
#     # 提示：根据你 EmbeddingClient 的具体实现，方法名可能是 embed_query 或 embed_documents
#     dense_vector = embed.embed_query(test_text)

#     logger.info(f"✅ 稠密向量生成成功，维度: {len(dense_vector)}")

#     # 4. 初始化你的 Milvus 异步管理器
#     milvus_config = MilvusConfig(
#         host=app_config.milvus.host,
#         port=app_config.milvus.port,
#         token=app_config.milvus.token,
#         collection_name=app_config.milvus.collection_name,
#         embedding_size=1024,
#     )
#     manager = MilvusClientManager(config=milvus_config)

#     # 5. 执行集合与双索引初始化（测试时建议设为 True 刷新集合）
#     logger.info("📡 正在异步初始化 Milvus 集合与双索引...")
#     await manager.init_collection_and_index(drop_old=True)

#     # 6. 调用你写的 add_document_async 异步函数插入数据
#     logger.info("📥 正在异步将数据及动态 Metadata 写入 Milvus...")
#     generated_ids = await manager.add_document_async(
#         text=test_text, vector=dense_vector, metadata=test_metadata
#     )

#     logger.info(f"🎉 数据插入成功！Milvus 自动生成的主键 ID 列表: {generated_ids}")

#     # 8. 优雅关闭客户端
#     await manager.close()
#     logger.info("🔌 Milvus 异步客户端已安全关闭。")


# if __name__ == "__main__":
#     # 使用 asyncio 驱动异步事件循环执行测试
#     asyncio.run(test_milvus_add_document())
