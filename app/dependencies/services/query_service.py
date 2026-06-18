from typing import Annotated

from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from pymilvus import AsyncMilvusClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.siliconflow_embeding_client import PureRequestsEmbeddings
from app.dependencies.infrastructure.db_session import get_dw_session, get_meta_session
from app.dependencies.infrastructure.embedding import get_embedding_client
from app.dependencies.infrastructure.es import get_es
from app.dependencies.infrastructure.milvus import get_milvus_client
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.milvus.column_milvus_repository import DataAgentColumnCollection
from app.repositories.milvus.metric_milvus_repository import MetricMilvusRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.services.query_service import QueryService


async def get_dw_mysql_repository(
    session: Annotated[AsyncSession, Depends(get_dw_session)],
):
    return DWMySQLRepository(session=session)


async def get_meta_mysql_repository(
    session: Annotated[AsyncSession, Depends(get_meta_session)],
):
    return MetaMySQLRepository(session=session)


async def get_column_milvus_repository(
    milvus_client: AsyncMilvusClient = Depends(get_milvus_client),
):
    return DataAgentColumnCollection(client=milvus_client)


async def get_metric_milvus_repository(
    milvus_client: AsyncMilvusClient = Depends(get_milvus_client),
):
    return MetricMilvusRepository(client=milvus_client)


async def get_value_es_repository(
    es_client: AsyncElasticsearch = Depends(get_es),
):
    return ValueESRepository(client=es_client)


async def query_service(
    dw_mysql_repository: DWMySQLRepository = Depends(get_dw_mysql_repository),
    meta_mysql_repository: MetaMySQLRepository = Depends(get_meta_mysql_repository),
    column_milvus_repository: DataAgentColumnCollection = Depends(
        get_column_milvus_repository
    ),
    metric_milvus_repository: MetricMilvusRepository = Depends(
        get_metric_milvus_repository
    ),
    embedding_client: PureRequestsEmbeddings = Depends(get_embedding_client),
    value_es_repository: ValueESRepository = Depends(get_value_es_repository),
):
    return QueryService(
        embedding_client=embedding_client,
        column_milvus_repository=column_milvus_repository,
        value_es_repository=value_es_repository,
        metric_milvus_repository=metric_milvus_repository,
        meta_mysql_repository=meta_mysql_repository,
        dw_mysql_repository=dw_mysql_repository,
    )
