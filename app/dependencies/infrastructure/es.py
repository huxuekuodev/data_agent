from elasticsearch import AsyncElasticsearch

from app.clients.es_client_manager import es_client_manager


def get_es() -> AsyncElasticsearch:
    return es_client_manager.client
