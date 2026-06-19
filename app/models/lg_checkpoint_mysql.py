from sqlalchemy import JSON, BigInteger, LargeBinary, String
from sqlalchemy.orm import mapped_column

from app.models.base import Base


class LGCheckpointModel(Base):
    __tablename__ = "lg_checkpoints"

    id = mapped_column(BigInteger, primary_key=True)

    thread_id = mapped_column(String(128))

    checkpoint_ns = mapped_column(String(128), default="")

    checkpoint_id = mapped_column(String(64))

    parent_checkpoint_id = mapped_column(String(64))

    checkpoint_data = mapped_column(LargeBinary)

    metadata_json = mapped_column(JSON)

    version = mapped_column(BigInteger, default=1)
