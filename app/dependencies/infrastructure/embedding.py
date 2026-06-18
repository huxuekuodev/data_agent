from app.clients.siliconflow_embeding_client import (
    PureRequestsEmbeddings,
    siliconFlowEmbeddingClient,
)


async def get_embedding_client() -> PureRequestsEmbeddings:
    return siliconFlowEmbeddingClient.embeddings
