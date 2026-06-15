from dataclasses import dataclass
from pathlib import Path

from omegaconf import OmegaConf

from app.conf.meta_config import MetaConfig
from app.entities.column_info import ColumnInfo
from app.entities.table_info import TableInfo
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository


@dataclass
class MetaKnowledgeService:

    dw_mysql_repository: DWMySQLRepository
    meta_mysql_repository: MetaMySQLRepository

    async def build(self, config_path: Path):
        """
        构建元知识库
        """
        context = OmegaConf.load(config_path)
        schema = OmegaConf.structured(MetaConfig)
        meta_config: MetaConfig = OmegaConf.to_object(OmegaConf.merge(schema, context))
        table_infos: list[TableInfo] = []
        column_infos: list[ColumnInfo] = []
        if meta_config.tables:
            for table in meta_config.tables:
                table_infos.append(
                    TableInfo(
                        id=table.name,
                        name=table.name,
                        role=table.role,
                        description=table.description,
                    )
                )
                table_columns = await self.dw_mysql_repository.get_column_types(
                    table.name
                )
                for column in table.columns:
                    column_values = await self.dw_mysql_repository.get_column_values(
                        table.name, column.name, 10
                    )
                    column_infos.append(
                        ColumnInfo(
                            id=f"{table.name}.{column.name}",
                            name=column.name,
                            description=column.description,
                            type=table_columns[column.name],
                            role=column.role,
                            table_id=table.name,
                            alias=column.alias,
                            examples=column_values,
                        )
                    )

        async with self.meta_mysql_repository.session.begin():
            await self.meta_mysql_repository.save_table_infos(table_infos)
            await self.meta_mysql_repository.save_column_infos(column_infos)

        # 存储到向量数据库

        if meta_config.metrics:
            pass
        pass
