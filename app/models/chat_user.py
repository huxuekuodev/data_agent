from datetime import datetime

from sqlalchemy import BigInteger, DateTime, SmallInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class ChatUser(Base):
    """
    聊天机器人用户表
    """

    __tablename__ = "chat_users"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True, comment="用户主键ID"
    )

    user_uuid: Mapped[str] = mapped_column(
        String(36), unique=True, nullable=False, comment="用户UUID"
    )

    username: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, comment="用户名"
    )

    nickname: Mapped[str | None] = mapped_column(
        String(64), nullable=True, comment="昵称"
    )

    email: Mapped[str | None] = mapped_column(
        String(255), nullable=True, unique=True, comment="邮箱"
    )

    mobile: Mapped[str | None] = mapped_column(
        String(32), nullable=True, unique=True, comment="手机号"
    )

    password_hash: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="密码哈希"
    )

    avatar_url: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="头像"
    )

    status: Mapped[int] = mapped_column(
        SmallInteger, default=1, nullable=False, comment="状态"
    )

    user_type: Mapped[int] = mapped_column(
        SmallInteger, default=1, nullable=False, comment="用户类型"
    )

    token_quota: Mapped[int] = mapped_column(
        BigInteger, default=0, nullable=False, comment="Token额度"
    )

    token_used: Mapped[int] = mapped_column(
        BigInteger, default=0, nullable=False, comment="已使用Token"
    )

    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="最后登录时间"
    )

    last_login_ip: Mapped[str | None] = mapped_column(
        String(64), nullable=True, comment="最后登录IP"
    )

    remark: Mapped[str | None] = mapped_column(
        String(500), nullable=True, comment="备注"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, comment="创建时间"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment="更新时间",
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, comment="软删除时间"
    )
