from datetime import date, datetime
from enum import StrEnum
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserRole(StrEnum):
    ADMIN = "admin"
    MODERATOR = "moderator"


class PromptType(StrEnum):
    IMAGE = "image"
    TEXT = "text"


class PostStatus(StrEnum):
    DRAFT = "draft"
    PREVIEW = "preview"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    CANCELLED = "cancelled"
    FAILED = "failed"


class GenerationType(StrEnum):
    IMAGE = "image"
    TEXT = "text"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255))
    full_name: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"
    __table_args__ = (UniqueConstraint("type", "version", name="uq_prompt_type_version"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(32), index=True)
    content: Mapped[str] = mapped_column(Text)
    version: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class BirthdayPerson(Base):
    __tablename__ = "birthday_persons"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255))
    position: Mapped[str] = mapped_column(String(255))
    branch: Mapped[str] = mapped_column(String(255))
    birth_date: Mapped[date] = mapped_column(Date)
    original_photo_file_id: Mapped[str] = mapped_column(String(512))
    generated_photo_path: Mapped[str | None] = mapped_column(String(1024))
    generated_photo_file_id: Mapped[str | None] = mapped_column(String(512))
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class BirthdayPost(Base):
    __tablename__ = "birthday_posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    publication_datetime: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    timezone: Mapped[str] = mapped_column(String(64), default="Asia/Tashkent")
    status: Mapped[str] = mapped_column(String(32), index=True)
    text: Mapped[str | None] = mapped_column(Text)
    text_is_manual: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    approved_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    publication_lock_until: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    members: Mapped[list["BirthdayPostMember"]] = relationship(
        back_populates="post", cascade="all, delete-orphan", lazy="selectin"
    )


class BirthdayPostMember(Base):
    __tablename__ = "birthday_post_members"
    __table_args__ = (UniqueConstraint("post_id", "person_id", name="uq_post_person"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("birthday_posts.id", ondelete="CASCADE"))
    person_id: Mapped[int] = mapped_column(ForeignKey("birthday_persons.id", ondelete="CASCADE"))
    sort_order: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    post: Mapped[BirthdayPost] = relationship(back_populates="members")
    person: Mapped[BirthdayPerson] = relationship(lazy="selectin")


class Setting(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(255), primary_key=True)
    value: Mapped[Any] = mapped_column(JSON)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(255), index=True)
    entity_type: Mapped[str | None] = mapped_column(String(255))
    entity_id: Mapped[int | None] = mapped_column(Integer)
    payload: Mapped[Any | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class GenerationLog(Base):
    __tablename__ = "generation_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    person_id: Mapped[int | None] = mapped_column(ForeignKey("birthday_persons.id"))
    post_id: Mapped[int | None] = mapped_column(ForeignKey("birthday_posts.id"))
    type: Mapped[str] = mapped_column(String(32))
    provider: Mapped[str] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32))
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PublicationLog(Base):
    __tablename__ = "publication_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("birthday_posts.id"))
    channel_id: Mapped[str] = mapped_column(String(255))
    telegram_message_ids: Mapped[Any | None] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(32))
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

