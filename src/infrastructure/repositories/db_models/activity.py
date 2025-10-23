from datetime import datetime
from typing import Optional, Self
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, String, delete, select, update, CheckConstraint
from sqlalchemy.dialects.postgresql import SMALLINT, UUID as pgUUID
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from structlog import get_logger

from exceptions.exc import (
    ActivityUpdateException,
    ActivityCreateException,
    ActivityDeleteException,
    ActivityGetException,
)
from schemas.dto.input.activity import InActivityDTO, InUpdateActivityDTO
from .base import BaseModel


logger = get_logger("ActivityModel")


class Activity(BaseModel):
    __tablename__ = "activities"
    __table_args__ = (
        CheckConstraint("depth_level IN (1, 2, 3)", name="ck_depth_level_valid"),
    )

    id: Mapped[UUID] = mapped_column(pgUUID, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    parent_id: Mapped[Optional[UUID]] = mapped_column(
        pgUUID, ForeignKey("activities.id", ondelete="CASCADE"), nullable=True
    )
    depth_level: Mapped[int] = mapped_column(SMALLINT, default=1)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=datetime.now, onupdate=datetime.now
    )

    parent: Mapped[Optional[Self]] = relationship(
        "Activity",
        remote_side="Activity.id",
        back_populates="children",
        lazy="joined",
    )

    children: Mapped[list[Self]] = relationship(
        "Activity",
        back_populates="parent",
        cascade="all, delete-orphan",
        lazy="select",
    )

    @staticmethod
    async def create(session: AsyncSession, data: list[InActivityDTO]) -> "Activity":
        try:
            stmt = pg_insert(Activity).values(data).returning(Activity.id)
            result = await session.execute(stmt)
            return result.scalars().all()
        except IntegrityError as exc:
            logger.warning("Activity already exists", exc_info=exc)
            raise
        except SQLAlchemyError as exc:
            logger.error("Error creating activity", exc_info=exc)
            raise ActivityCreateException

    @staticmethod
    async def get_by_id(session: AsyncSession, activity_id: UUID) -> Optional["Activity"]:
        try:
            stmt = select(Activity).where(Activity.id == activity_id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"Error getting activity by id {activity_id}", exc_info=exc)
            raise ActivityGetException

    @staticmethod
    async def update(session: AsyncSession, activity_id: UUID, data: InUpdateActivityDTO) -> Optional[UUID]:
        try:
            stmt = update(Activity).where(Activity.id == activity_id).values(data).returning(Activity.id)
            row = (await session.execute(stmt)).scalar_one_or_none()
            return row
        except SQLAlchemyError as exc:
            logger.error(f"Error updating activity {activity_id}", exc_info=exc)
            raise ActivityUpdateException

    @staticmethod
    async def delete(session: AsyncSession, activity_id: UUID) -> Optional[UUID]:
        try:
            stmt = delete(Activity).where(Activity.id == activity_id).returning(Activity.id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"Error deleting activity {activity_id}", exc_info=exc)
            raise ActivityDeleteException

    @staticmethod
    async def get_all(session: AsyncSession) -> list["Activity"] | None:
        try:
            stmt = select(Activity)
            result = await session.execute(stmt)
            return result.scalars().all()
        except SQLAlchemyError as exc:
            logger.error("Error getting activities", exc_info=exc)
            raise ActivityGetException