from pymilvus import connections, utility


class BaseCollection:
    name = ""

    async def load(self, client):
        pass
