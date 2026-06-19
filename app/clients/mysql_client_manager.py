from dataclasses import dataclass, field

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.conf.app_config import DBConfig, app_config


@dataclass
class MySQLClientManager:
    engine: AsyncEngine = field(default=None, init=False)  # Engine 维护数据库连接池
    session_factory: async_sessionmaker = field(default=None, init=False)
    config: DBConfig

    # init 后初始化 engine
    def __post_init__(self):
        # https://docs.sqlalchemy.org/en/20/core/engines.html#sqlalchemy.create_engine
        self.engine = create_async_engine(
            url=f"mysql+asyncmy://{self.config.user}:{self.config.password}@{self.config.host}:{self.config.port}/{self.config.database}",
            pool_size=10,  # 连接池大小
            max_overflow=20,  # 最大溢出连接数
            pool_pre_ping=True,  # 每次获取连接时都检查连接是否有效
        )
        self.session_factory = async_sessionmaker(
            self.engine, expire_on_commit=False, autoflush=True
        )

    async def close(self):
        await self.engine.dispose()


dw_mysql_client_manager = MySQLClientManager(config=app_config.db_dw)
meta_mysql_client_manager = MySQLClientManager(config=app_config.db_meta)
data_agent_server_mysql_client_manager = MySQLClientManager(
    config=app_config.db_data_agent_server
)


async def test():
    async with dw_mysql_client_manager.session_factory() as session:
        result = await session.execute(text("SELECT * from fact_order limit 10"))
        # rows = result.fetchall() 返回元组
        rows = result.mappings().fetchall()  # 返回字典
        print(rows)
        pass


if __name__ == "__main__":
    import asyncio

    asyncio.run(test())
