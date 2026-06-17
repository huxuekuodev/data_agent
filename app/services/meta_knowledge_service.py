from dataclasses import dataclass
from pathlib import Path
import uuid

from attr import asdict
from omegaconf import OmegaConf

from app.conf.meta_config import MetaConfig
from app.entities.column_info import ColumnInfo
from app.entities.table_info import TableInfo
from app.entities.vector_info import VectorInfo
from app.repositories.es import value_es_repository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository
from app.conf.meta_config import TableConfig
from app.clients.siliconflow_embeding_client import siliconFlowEmbeddingClient
from app.repositories.es.value_es_repository import ValueESRepository
from app.entities.value_info import ValueInfo
from app.repositories.milvus.column_milvus_repository import DataAgentColumnCollection



@dataclass
class MetaKnowledgeService:

    dw_mysql_repository: DWMySQLRepository
    meta_mysql_repository: MetaMySQLRepository
    value_es_repository: ValueESRepository
    column_milvus_repository: DataAgentColumnCollection
    

    async def get_table_data(self,tables:list[TableConfig]):
        """
            获取元数据表数据
            :param tables:
            :return:     表信息、列信息、向量信息、值信息
        """
        table_infos: list[TableInfo] = []
        column_infos: list[ColumnInfo] = []
        vector_infos:list[VectorInfo] = []
        value_infos:list[ValueInfo] = []
        for table in tables:
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
                # 同步列值
                if column.sync:
                    es_column_values = await self.dw_mysql_repository.get_column_values(
                        table.name, column.name, 100000
                    )
                    value_infos.extend([ValueInfo(
                        id= f"{table.name}.{column.name}.{value}",
                        value=value,
                        column_id=f"{table.name}.{column.name}"
                    ) for value in es_column_values])

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
                vector_infos.append(
                    VectorInfo(
                        id= str(uuid.uuid4()),
                        embeding_text=column.name,
                        metadata=asdict(column)
                    )
                )
                vector_infos.append(
                    VectorInfo(
                        id= str(uuid.uuid4()),
                        embeding_text=column.description,
                        metadata=asdict(column)
                    )
                )
                for alia in column.alias:
                    vector_infos.append(
                        VectorInfo(
                            id= str(uuid.uuid4()),
                            embeding_text=alia,
                            metadata=asdict(column)
                        )
                    )
        return table_infos,column_infos,vector_infos,value_infos

    # 构建元知识库
    async def build(self, config_path: Path):
        """
        构建元知识库
        """
        context = OmegaConf.load(config_path)
        schema = OmegaConf.structured(MetaConfig)
        meta_config: MetaConfig = OmegaConf.to_object(OmegaConf.merge(schema, context))
        if meta_config.tables:
            table_infos,column_infos,vector_infos,value_infos = await self.get_table_data(meta_config.tables)
            async with self.meta_mysql_repository.session.begin():
                await self.meta_mysql_repository.save_table_infos(table_infos)
                await self.meta_mysql_repository.save_column_infos(column_infos)
            # 存储到向量数据库
            await self.create_milvus_data(vector_infos)
            # 存ES
            await self.value_es_repository.ensure_index()
            await self.value_es_repository.index(value_infos)
            

        if meta_config.metrics:
            pass
        pass


    async def create_milvus_data(self, vector_infos: list[VectorInfo],batch_size: int = 20):
        """
        创建向量数据库
        """
        for i in range(0,len(vector_infos),batch_size):
            batch = vector_infos[i:i+batch_size]
            # 获取文本向量
            embiding_list = await siliconFlowEmbeddingClient.embeddings.aembed_documents([info.embeding_text for info in batch])
            # 存储到向量数据库 TODO
            # await self.milvus_repository.create_vector(embiding_list)
            await self.column_milvus_repository.insert(batch)
