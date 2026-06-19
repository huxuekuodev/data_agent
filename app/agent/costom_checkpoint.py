from typing import AsyncIterator

from langgraph.checkpoint.base import BaseCheckpointSaver, CheckpointTuple
from sqlalchemy import desc, select

from app.clients.mysql_client_manager import data_agent_server_mysql_client_manager
from app.core.log import logger
from app.models.lg_checkpoint_mysql import LGCheckpointModel
from app.models.lg_checkpoint_writes_mysql import CheckpointWriteModel


class AsyncMySQLCheckpointSaver(BaseCheckpointSaver):
    def __init__(self):

        self.session_factory = data_agent_server_mysql_client_manager.session_factory

    async def aput(
        self,
        config,
        checkpoint,
        metadata,
        new_versions,
    ):
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        parent_checkpoint_id = config["configurable"].get("checkpoint_id")
        logger.info(f"调用aput 写入checkpoint: {thread_id}")
        async with self.session_factory() as session:

            try:
                row = LGCheckpointModel(
                    thread_id=thread_id,
                    checkpoint_ns=checkpoint_ns,
                    checkpoint_id=checkpoint["id"],
                    parent_checkpoint_id=parent_checkpoint_id,
                    checkpoint_data=Serializer.dumps(checkpoint),
                    metadata_json=metadata,
                )

                session.add(row)

                await session.commit()
            except Exception as e:
                logger.error(f"写入checkpoint失败: {e}")
                raise e

        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": checkpoint["id"],
            }
        }

    async def aget_tuple(
        self,
        config,
    ):
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = config["configurable"].get("checkpoint_id")
        logger.info(f"调用aget_tuple 读取checkpoint: {thread_id}")

        async with self.session_factory() as session:
            try:
                stmt = select(LGCheckpointModel).where(
                    LGCheckpointModel.thread_id == thread_id,
                    LGCheckpointModel.checkpoint_ns == checkpoint_ns,
                )

                if checkpoint_id:
                    stmt = stmt.where(LGCheckpointModel.checkpoint_id == checkpoint_id)
                else:
                    stmt = stmt.order_by(desc(LGCheckpointModel.id)).limit(1)

                result = await session.execute(stmt)
                row = result.scalar_one_or_none()

                if row is None:
                    return None

                checkpoint = Serializer.loads(row.checkpoint_data)

                return CheckpointTuple(
                    config=config,
                    checkpoint=checkpoint,
                    metadata=row.metadata_json or {},
                    parent_config=None,
                    pending_writes=[],
                )
            except Exception as e:
                logger.error(f"读取checkpoint失败: {e}")
                raise e

    async def aput_writes(
        self,
        config,
        writes,
        task_id,
    ):
        thread_id = config["configurable"]["thread_id"]
        checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
        checkpoint_id = config["configurable"]["checkpoint_id"]
        logger.info(f"调用aput_writes 写入checkpoint writes: {thread_id}")

        rows = []
        for channel, value in writes:
            rows.append(
                CheckpointWriteModel(
                    thread_id=thread_id,
                    checkpoint_ns=checkpoint_ns,
                    checkpoint_id=checkpoint_id,
                    task_id=task_id,
                    channel_name=channel,
                    write_data=Serializer.dumps(value),
                )
            )

        async with self.session_factory() as session:
            try:
                session.add_all(rows)
                await session.commit()
            except Exception as e:
                logger.error(f"写入checkpoint writes失败: {e}")
                raise e

    async def alist(
        self,
        config=None,
        *,
        filter=None,
        before=None,
        limit=100,
    ) -> AsyncIterator:
        async with self.session_factory() as session:
            try:
                stmt = (
                    select(LGCheckpointModel)
                    .order_by(desc(LGCheckpointModel.id))
                    .limit(limit)
                )

                result = await session.stream(stmt)

                async for row in result.scalars():
                    try:
                        yield CheckpointTuple(
                            config={
                                "configurable": {
                                    "thread_id": row.thread_id,
                                    "checkpoint_ns": row.checkpoint_ns,
                                    "checkpoint_id": row.checkpoint_id,
                                }
                            },
                            checkpoint=Serializer.loads(row.checkpoint_data),
                            metadata=row.metadata_json or {},
                            parent_config=None,
                            pending_writes=[],
                        )
                    except Exception as e:
                        logger.error(f"解析checkpoint数据失败: {e}")
                        continue
            except Exception as e:
                logger.error(f"查询checkpoint列表失败: {e}")
                raise e


import zstandard as zstd
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

serde = JsonPlusSerializer()

compressor = zstd.ZstdCompressor(level=3)
decompressor = zstd.ZstdDecompressor()


import pickle


class Serializer:

    @staticmethod
    def dumps(obj):
        try:
            payload = serde.dumps_typed(obj)
            return compressor.compress(pickle.dumps(payload))
        except Exception as e:
            logger.error(f"序列化对象失败: {e}")
            raise e

    @staticmethod
    def loads(data):
        try:
            payload = pickle.loads(decompressor.decompress(data))
            return serde.loads_typed(payload)
        except Exception as e:
            logger.error(f"反序列化数据失败: {e}")
            raise e
