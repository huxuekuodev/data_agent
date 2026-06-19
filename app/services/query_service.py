import json

from langchain_core.runnables import RunnableConfig

from app.agent.context import DataAgentContext
from app.agent.graph import graph
from app.clients.siliconflow_embeding_client import PureRequestsEmbeddings
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.milvus.column_milvus_repository import DataAgentColumnCollection
from app.repositories.milvus.metric_milvus_repository import MetricMilvusRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository


class QueryService:
    def __init__(
        self,
        embedding_client: PureRequestsEmbeddings,
        column_milvus_repository: DataAgentColumnCollection,
        value_es_repository: ValueESRepository,
        metric_milvus_repository: MetricMilvusRepository,
        meta_mysql_repository: MetaMySQLRepository,
        dw_mysql_repository: DWMySQLRepository,
    ):
        self.embedding_client = embedding_client
        self.column_milvus_repository = column_milvus_repository
        self.value_es_repository = value_es_repository
        self.metric_milvus_repository = metric_milvus_repository
        self.meta_mysql_repository = meta_mysql_repository
        self.dw_mysql_repository = dw_mysql_repository

    async def query(self, query: str, user_uuid: str):
        """
        执行查询

        Args:
            query: 用户查询内容
            user_uuid: 用户唯一标识（从 token 中解析）
        """
        try:
            config: RunnableConfig = {"configurable": {"thread_id": user_uuid}}
            async for chunk in graph.astream(
                {"query": query},
                config=config,
                context=DataAgentContext(
                    embedding_client=self.embedding_client,
                    column_milvus_repository=self.column_milvus_repository,
                    metric_milvus_repository=self.metric_milvus_repository,
                    value_es_repository=self.value_es_repository,
                    meta_mysql_repository=self.meta_mysql_repository,
                    dw_mysql_repository=self.dw_mysql_repository,
                ),
                stream_mode="custom",
            ):
                yield f"data: {json.dumps(chunk, ensure_ascii=False, default=str)}\n\n"  # SSE格式发送数据
        except Exception as e:
            yield f"data: {json.dumps({'type': 'error', 'message': str(e)}, ensure_ascii=False, default=str)}\n\n"
