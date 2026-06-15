from dataclasses import dataclass
from pathlib import Path

from omegaconf import OmegaConf

from app.conf.meta_config import MetaConfig


@dataclass
class MetaKnowledgeService:

    async def build(self, config_path: Path):
        """
        构建元知识库
        """
        context = OmegaConf.load(config_path)
        schema = OmegaConf.structured(MetaConfig)
        meta_config: MetaConfig = OmegaConf.to_object(OmegaConf.merge(schema, context))

        if meta_config.tables:
            pass

        if meta_config.metrics:
            pass
        pass
