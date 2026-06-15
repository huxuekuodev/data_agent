import argparse
import asyncio
from pathlib import Path

from app.services.meta_knowledge_service import MetaKnowledgeService

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="build_meta_knowledge")
    parser.add_argument(
        "--config_path", type=str, required=True, help="Path to the config file"
    )
    args = parser.parse_args()
    config_path = Path(args.config_path)

    meta_knowledge_service = MetaKnowledgeService()
    asyncio.run(meta_knowledge_service.build(config_path))
