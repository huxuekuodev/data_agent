from pymilvus import AsyncMilvusClient

from app.core.log import logger
from pymilvus import DataType, Field, Function, FunctionType
from app.repositories.milvus.base_collection import BaseCollection
from app.core.models import VectorInfo


class DataAgentColumnCollection(BaseCollection):
    
    name = "data-agent-column"

    async def load(self):
        has = await self.has_collection()
        if has:
            await self.client.load_collection(self.name)
        await self._create_collection()
        await self.client.load_collection(self.name)

    async def _create_collection(self):
        schema = self.client.create_schema(
            enable_dynamic_field=True,
        )
        bm25_function = Function(
            name="text_bm25_emb", # Function name
            input_field_names=["text"], # Name of the VARCHAR field containing raw text data
            output_field_names=["sparse_vector"], # Name of the SPARSE_FLOAT_VECTOR field reserved to store generated embeddings
            function_type=FunctionType.BM25, # Set to `BM25`
        )
        schema.add_function(bm25_function)
        schema.add_field(field_name="id",datatype=DataType.INT64,is_primary=True,auto_id=True,)
        schema.add_field(field_name="sparse_vector", datatype=DataType.SPARSE_FLOAT_VECTOR)
        schema.add_field(field_name="text", datatype=DataType.VARCHAR,enable_analyzer=True,analyzer_params = {
            "type": "chinese",
        })
        schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=1024)
        index_param = await self._index_param()
        self.client.create_collection(
            collection_name=self.name,
            schema=schema,
            index_params= index_param,
        )
        pass

    async def _index_param(self):
        index_params = self.client.prepare_index_params()
        # 创建向量索引
        index_params.add_index(
            field_name="vector", # Name of the vector field to be indexed
            index_type="HNSW", # Type of the index to create
            index_name="vector_index", # Name of the index to create
            metric_type="COSINE", # Metric type used to measure similarity
            params={
                "M": 64, # Maximum number of neighbors each node can connect to in the graph
                "efConstruction": 100 # Number of candidate neighbors considered for connection during index construction
            } # Index building params
        )
        # 创建稀疏索引
        index_params.add_index(
            field_name="sparse_vector",
            index_type="SPARSE_INVERTED_INDEX",
            metric_type="BM25",
            params={
                "inverted_index_algo": "DAAT_MAXSCORE",
                "bm25_k1": 1.2,
                "bm25_b": 0.75
            }
        )
        return index_params

    async def create(self, vector_infos: list[VectorInfo],batch_size: int = 20):
        """
            创建向量数据
        """
        self.client.insert()
        await self.client.insert(
            collection_name=self.name,
            data=vector_infos,
            batch_size=batch_size,
        )