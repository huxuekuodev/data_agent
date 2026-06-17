import argparse
import asyncio
from pathlib import Path

from app.clients.es_client_manager import es_client_manager
from app.clients.milvus_client_manager import milvus_client_manager
from app.clients.mysql_client_manager import (
    dw_mysql_client_manager,
    meta_mysql_client_manager,
)
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.milvus.column_milvus_repository import DataAgentColumnCollection
from app.repositories.milvus.metric_milvus_repository import MetricMilvusRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.services.meta_knowledge_service import MetaKnowledgeService


async def run(config_path: Path):
    client = await milvus_client_manager.get_client()
    async with dw_mysql_client_manager.session_factory() as dw_session:
        async with meta_mysql_client_manager.session_factory() as meta_session:
            meta_knowledge_service = MetaKnowledgeService(
                dw_mysql_repository=DWMySQLRepository(session=dw_session),
                value_es_repository=ValueESRepository(client=es_client_manager.client),
                column_milvus_repository=DataAgentColumnCollection(client=client),
                metric_milvus_repository=MetricMilvusRepository(client=client),
                meta_mysql_repository=MetaMySQLRepository(session=meta_session),
            )
            await meta_knowledge_service.build(config_path)
            await dw_session.commit()
            await meta_session.commit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="build_meta_knowledge")
    parser.add_argument(
        "--config_path", type=str, required=True, help="Path to the config file"
    )
    args = parser.parse_args()
    config_path = Path(args.config_path)

    asyncio.run(run(config_path=config_path))
