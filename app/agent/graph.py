import asyncio

from langchain_core.runnables import RunnableConfig
from langgraph.constants import END, START
from langgraph.graph import StateGraph

from app.agent.context import DataAgentContext
from app.agent.costom_checkpoint import AsyncMySQLCheckpointSaver
from app.agent.nodes.add_extra_context import add_extra_context
from app.agent.nodes.correct_sql import correct_sql
from app.agent.nodes.execute_sql import execute_sql
from app.agent.nodes.extract_keywords import extract_keywords
from app.agent.nodes.filter_metric import filter_metric
from app.agent.nodes.filter_table import filter_table
from app.agent.nodes.generate_sql import generate_sql
from app.agent.nodes.merge_retrieved_info import merge_retrieved_info
from app.agent.nodes.recall_column import recall_column
from app.agent.nodes.recall_metric import recall_metric
from app.agent.nodes.recall_value import recall_value
from app.agent.nodes.validate_sql import validate_sql
from app.agent.state import DataAgentState
from app.clients import siliconflow_embeding_client
from app.clients.es_client_manager import es_client_manager
from app.clients.milvus_client_manager import milvus_client_manager
from app.clients.mysql_client_manager import (
    dw_mysql_client_manager,
    meta_mysql_client_manager,
)
from app.clients.siliconflow_embeding_client import siliconFlowEmbeddingClient
from app.repositories.es.value_es_repository import ValueESRepository
from app.repositories.milvus.column_milvus_repository import DataAgentColumnCollection
from app.repositories.milvus.metric_milvus_repository import MetricMilvusRepository
from app.repositories.mysql.dw.dw_mysql_repository import DWMySQLRepository
from app.repositories.mysql.meta.meta_mysql_repository import MetaMySQLRepository

graph_builder = StateGraph(state_schema=DataAgentState, context_schema=DataAgentContext)

# 添加节点
graph_builder.add_node("extract_keywords", extract_keywords)
graph_builder.add_node("recall_column", recall_column)
graph_builder.add_node("recall_value", recall_value)
graph_builder.add_node("recall_metric", recall_metric)
graph_builder.add_node("merge_retrieved_info", merge_retrieved_info)
graph_builder.add_node("filter_metric", filter_metric)
graph_builder.add_node("filter_table", filter_table)
graph_builder.add_node("add_extra_context", add_extra_context)
graph_builder.add_node("generate_sql", generate_sql)
graph_builder.add_node("validate_sql", validate_sql)
graph_builder.add_node("correct_sql", correct_sql)
graph_builder.add_node("execute_sql", execute_sql)

# 添加关系
graph_builder.add_edge(START, "extract_keywords")
graph_builder.add_edge("extract_keywords", "recall_column")
graph_builder.add_edge("extract_keywords", "recall_value")
graph_builder.add_edge("extract_keywords", "recall_metric")
graph_builder.add_edge("recall_column", "merge_retrieved_info")
graph_builder.add_edge("recall_value", "merge_retrieved_info")
graph_builder.add_edge("recall_metric", "merge_retrieved_info")
graph_builder.add_edge("merge_retrieved_info", "filter_table")
graph_builder.add_edge("merge_retrieved_info", "filter_metric")
graph_builder.add_edge("filter_table", "add_extra_context")
graph_builder.add_edge("filter_metric", "add_extra_context")
graph_builder.add_edge("add_extra_context", "generate_sql")
graph_builder.add_edge("generate_sql", "validate_sql")

graph_builder.add_conditional_edges(
    "validate_sql",
    lambda state: "execute_sql" if state["error"] is None else "correct_sql",
    {"execute_sql": "execute_sql", "correct_sql": "correct_sql"},
)

graph_builder.add_edge("correct_sql", "execute_sql")
graph_builder.add_edge("execute_sql", END)

checkpoint_saver = AsyncMySQLCheckpointSaver()

graph = graph_builder.compile(checkpointer=checkpoint_saver)


if __name__ == "__main__":

    async def run_test():
        milvusClient = await milvus_client_manager.get_client()
        async with (
            meta_mysql_client_manager.session_factory() as meta_session,
            dw_mysql_client_manager.session_factory() as dw_mysql_session,
        ):
            config: RunnableConfig = {"configurable": {"thread_id": "1"}}
            result = await graph.ainvoke(
                {"query": "统计华北地区的销售总额"},
                config=config,
                context=DataAgentContext(
                    embedding_client=siliconFlowEmbeddingClient.embeddings,
                    column_milvus_repository=DataAgentColumnCollection(milvusClient),
                    metric_milvus_repository=MetricMilvusRepository(milvusClient),
                    value_es_repository=ValueESRepository(es_client_manager.client),
                    meta_mysql_repository=MetaMySQLRepository(session=meta_session),
                    dw_mysql_repository=DWMySQLRepository(session=dw_mysql_session),
                ),
            )
        # print(result)
        pass

    asyncio.run(run_test())
