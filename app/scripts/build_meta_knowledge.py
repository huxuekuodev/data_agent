import argparse
import asyncio
from pathlib import Path

from app.clients.mysql_client_manager import dw_mysql_client_manager
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.services.meta_knowledge_service import MetaKnowledgeService


async def run(config_path: Path):
    async with dw_mysql_client_manager.session_factory() as session:
        meta_knowledge_service = MetaKnowledgeService(
            dw_mysql_repository=DWMySQLRepository(session=session)
        )
        await meta_knowledge_service.build(config_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="build_meta_knowledge")
    parser.add_argument(
        "--config_path", type=str, required=True, help="Path to the config file"
    )
    args = parser.parse_args()
    config_path = Path(args.config_path)
    asyncio.run(run(config_path=config_path))
