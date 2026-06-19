from datetime import datetime

from sqlalchemy import BigInteger, DateTime, LargeBinary, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.models.base import Base


class CheckpointWriteModel(Base):
    __tablename__ = "lg_checkpoint_writes"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="主键ID"
    )

    thread_id: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="线程ID"
    )

    checkpoint_ns: Mapped[str] = mapped_column(
        String(128), nullable=False, default="", comment="命名空间"
    )

    checkpoint_id: Mapped[str] = mapped_column(
        String(64), nullable=False, comment="CheckpointID"
    )

    task_id: Mapped[str] = mapped_column(String(128), nullable=False, comment="Task ID")

    channel_name: Mapped[str] = mapped_column(
        String(128), nullable=False, comment="Channel名称"
    )

    write_data: Mapped[bytes] = mapped_column(
        LargeBinary, nullable=False, comment="序列化后的数据"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        comment="创建时间",
        server_default=func.now(),
    )
