import traceback
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path

from omegaconf import OmegaConf

from app.clients.siliconflow_embeding_client import siliconFlowEmbeddingClient
from app.conf.meta_config import MetaConfig, MetricConfig, TableConfig
from app.core.decorators import timing
from app.core.log import logger
from app.entities.column_info import ColumnInfo
from app.entities.column_metric import ColumnMetric
from app.entities.metric_info import MetricInfo
from app.entities.table_info import TableInfo
from app.entities.value_info import ValueInfo
from app.entities.vector_info import VectorInfo
from app.repositories.es import value_es_repository
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.milvus.column_milvus_repository import DataAgentColumnCollection
from app.repositories.milvus.metric_milvus_repository import MetricMilvusRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository


@dataclass
class MetaKnowledgeService:

    dw_mysql_repository: DWMySQLRepository
    meta_mysql_repository: MetaMySQLRepository
    value_es_repository: ValueESRepository
    column_milvus_repository: DataAgentColumnCollection
    metric_milvus_repository: MetricMilvusRepository

    async def get_table_data(self, tables: list[TableConfig]):
        """
        获取元数据表数据
        :param tables:
        :return:     表信息、列信息、向量信息、值信息
        """
        try:
            table_infos: list[TableInfo] = []
            column_infos: list[ColumnInfo] = []
            vector_infos: list[VectorInfo] = []
            value_infos: list[ValueInfo] = []
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
                        es_column_values = (
                            await self.dw_mysql_repository.get_column_values(
                                table.name, column.name, 100000
                            )
                        )
                        value_infos.extend(
                            [
                                ValueInfo(
                                    id=f"{table.name}.{column.name}.{value}",
                                    value=value,
                                    column_id=f"{table.name}.{column.name}",
                                )
                                for value in es_column_values
                            ]
                        )

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
                            id=str(uuid.uuid4()),
                            embeding_text=column.name,
                            metadata=asdict(column),
                        )
                    )
                    vector_infos.append(
                        VectorInfo(
                            id=str(uuid.uuid4()),
                            embeding_text=column.description,
                            metadata=asdict(column),
                        )
                    )
                    for alia in column.alias:
                        vector_infos.append(
                            VectorInfo(
                                id=str(uuid.uuid4()),
                                embeding_text=alia,
                                metadata=asdict(column),
                            )
                        )
        except Exception as e:
            logger.error(f"获取元数据表数据失败: {e}, 栈信息:{traceback.format_exc()}")
            return [], [], [], []
        return table_infos, column_infos, vector_infos, value_infos

    async def _save_db_metrics_data(self, metrics: list[MetricConfig]):
        metric_infos: list[MetricInfo] = []
        column_metrics: list[ColumnMetric] = []
        vector_infos: list[VectorInfo] = []
        for metric in metrics:
            # 构造MetricInfo数据
            metric_info = MetricInfo(
                id=metric.name,
                name=metric.name,
                description=metric.description,
                relevant_columns=metric.relevant_columns,
                alias=metric.alias,
            )
            metric_infos.append(metric_info)

            # 构造VectorInfo数据
            vector_infos.append(
                VectorInfo(
                    id=str(uuid.uuid4()),
                    embeding_text=metric.name,
                    metadata=asdict(metric_info),
                )
            )

            # 构造VectorInfo数据
            vector_infos.append(
                VectorInfo(
                    id=str(uuid.uuid4()),
                    embeding_text=metric.description,
                    metadata=asdict(metric_info),
                )
            )

            # 构造VectorInfo数据
            for alia in metric.alias:
                vector_infos.append(
                    VectorInfo(
                        id=str(uuid.uuid4()),
                        embeding_text=alia,
                        metadata=asdict(metric_info),
                    )
                )

            for relevant_column in metric.relevant_columns:
                # 构造ColumnMetric数据
                column_metric = ColumnMetric(
                    column_id=relevant_column, metric_id=metric.name
                )
                column_metrics.append(column_metric)
        # 保存到元数据数据库
        await self.meta_mysql_repository.save_metric_infos(metric_infos)
        await self.meta_mysql_repository.save_column_metrics(column_metrics)
        return vector_infos

        pass

    # 构建元知识库
    async def build(self, config_path: Path):
        """
        构建元知识库
        """
        context = OmegaConf.load(config_path)
        schema = OmegaConf.structured(MetaConfig)
        meta_config: MetaConfig = OmegaConf.to_object(OmegaConf.merge(schema, context))
        # if meta_config.tables:
        #     table_infos, column_infos, vector_infos, value_infos = (
        #         await self.get_table_data(meta_config.tables)
        #     )
        #     if (
        #         not table_infos
        #         or not column_infos
        #         or not vector_infos
        #         or not value_infos
        #     ):
        #         logger.error("获取元数据表数据失败")
        #         return

        #     # 存储到 MySQL数据库
        #     await self.meta_mysql_repository.save_table_infos(table_infos)
        #     await self.meta_mysql_repository.save_column_infos(column_infos)
        #     # 存储到向量数据库
        #     await self.create_milvus_data(vector_infos)
        #     # # 存储到 Elasticsearch数据库
        #     await self.value_es_repository.ensure_index()
        #     await self.value_es_repository.index(value_infos)
        #     logger.info("元数据表数据构建完成")

        if meta_config.metrics:
            vector_infos = await self._save_db_metrics_data(meta_config.metrics)
            # 存储到向量数据库
            await self.create_metric_milvus_data(vector_infos)
            logger.info("元数据指标数据构建完成")

    @timing
    async def create_milvus_data(
        self, vector_infos: list[VectorInfo], batch_size: int = 20
    ):
        """
        创建向量数据库
        """
        await self.column_milvus_repository.load()
        for i in range(0, len(vector_infos), batch_size):
            batch = vector_infos[i : i + batch_size]
            # 获取文本向量
            embiding_list = (
                await siliconFlowEmbeddingClient.embeddings.aembed_documents(
                    [info.embeding_text for info in batch]
                )
            )
            # 存储到向量数据库
            await self.column_milvus_repository.insert(
                [
                    {
                        "text": info.embeding_text,
                        "vector": embed,
                        "metadata": info.metadata,
                    }
                    for info, embed in zip(batch, embiding_list)
                ]
            )

    @timing
    async def create_metric_milvus_data(
        self, vector_infos: list[VectorInfo], batch_size: int = 20
    ):
        """
        创建向量数据库
        """
        await self.metric_milvus_repository.load()
        for i in range(0, len(vector_infos), batch_size):
            batch = vector_infos[i : i + batch_size]
            # 获取文本向量
            embiding_list = (
                await siliconFlowEmbeddingClient.embeddings.aembed_documents(
                    [info.embeding_text for info in batch]
                )
            )
            # 存储到向量数据库
            await self.metric_milvus_repository.insert(
                [
                    {
                        "text": info.embeding_text,
                        "vector": embed,
                        "metadata": info.metadata,
                    }
                    for info, embed in zip(batch, embiding_list)
                ]
            )
