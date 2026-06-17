from typing import TypedDict

from app.clients.siliconflow_embeding_client import PureRequestsEmbeddings
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.milvus.column_milvus_repository import DataAgentColumnCollection
from app.repositories.milvus.metric_milvus_repository import MetricMilvusRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository


class DataAgentContext(TypedDict):
    embedding_client: PureRequestsEmbeddings
    # column_qdrant_repository: ColumnQdrantRepository
    column_milvus_repository: DataAgentColumnCollection
    value_es_repository: ValueESRepository
    # metric_qdrant_repository: MetricQdrantRepository
    metric_milvus_repository: MetricMilvusRepository
    meta_mysql_repository: MetaMySQLRepository
    dw_mysql_repository: DWMySQLRepository
