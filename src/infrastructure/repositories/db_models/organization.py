from datetime import datetime
from typing import Optional
from uuid import UUID

from geoalchemy2.shape import from_shape
from shapely.geometry import Point as ShapelyPoint
from sqlalchemy import DateTime, ForeignKey, String, delete, func, select, update
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship, selectinload
from structlog import get_logger

from exceptions.exc import (
    OrganizationAlreadyExistsException,
    OrganizationCreateException,
    OrganizationDeleteException,
    OrganizationGetException,
    OrganizationPaginException,
    OrganizationUpdateException,
)
from schemas.dto.input.organization import InOrganizationDTO, InOrganizationFiltersDTO, InOrganizationUpdateDTO
from schemas.dto.output.organization import OutOrganizationDTO, OutOrganizationPaginationDTO
from schemas.enums.order import OrderByOrganization, OrderByType

from .base import BaseModel
from .point import Point

logger = get_logger("OrganizationModels")


class Organization(BaseModel):
    __tablename__ = "organizations"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    phone_number: Mapped[str] = mapped_column(String, nullable=False)
    point_id: Mapped[UUID] = mapped_column(pgUUID, ForeignKey("points.id", ondelete="RESTRICT"), nullable=False)
    activity_ids: Mapped[list[UUID]] = mapped_column(ARRAY(pgUUID(as_uuid=True)), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.now, onupdate=datetime.now)

    point: Mapped["Point"] = relationship(
        "Point",
        back_populates="organizations",
        lazy="joined",
    )

    activities: Mapped[list["Activity"]] = relationship(  # noqa: F821
        "Activity",
        primaryjoin="Activity.id == any_(foreign(Organization.activity_ids))",
        lazy="select",
        viewonly=True,
        uselist=True,
    )

    @staticmethod
    async def create(session: AsyncSession, data: list[InOrganizationDTO]) -> Optional[list[UUID]]:
        try:
            stmt = pg_insert(Organization).values(data).returning(Organization.id)
            result = await session.execute(stmt)
            rows = result.scalars().all()
            return rows
        except IntegrityError as exc:
            logger.warning("Organization with such already exists", exc_info=exc)
            raise OrganizationAlreadyExistsException from exc
        except SQLAlchemyError as exc:
            logger.error("Error creating organization", exc_info=exc)
            raise OrganizationCreateException from exc

    @staticmethod
    async def get_by_id(session: AsyncSession, org_id: UUID) -> Optional[OutOrganizationDTO]:
        try:
            stmt = select(Organization).where(Organization.id == org_id)
            result = await session.execute(stmt)
            row = result.scalar_one_or_none()
            return OutOrganizationDTO.model_validate(row) if row else None
        except SQLAlchemyError as exc:
            logger.error(f"Error getting organization by id {org_id}", exc_info=exc)
            raise OrganizationGetException from exc

    @staticmethod
    async def update(session: AsyncSession, org_id: UUID, data: InOrganizationUpdateDTO) -> Optional[UUID]:
        try:
            stmt = update(Organization).where(Organization.id == org_id).values(data).returning(Organization.id)
            row = (await session.execute(stmt)).scalar_one_or_none()
            return row
        except SQLAlchemyError as exc:
            logger.error(f"Error updating organization {org_id}", exc_info=exc)
            raise OrganizationUpdateException from exc

    @staticmethod
    async def delete(session: AsyncSession, org_id: UUID) -> Optional[UUID]:
        try:
            stmt = delete(Organization).where(Organization.id == org_id).returning(Organization.id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"Error deleting organization {org_id}", exc_info=exc)
            raise OrganizationDeleteException from exc

    @staticmethod
    async def get_with_pagination(
        session: AsyncSession, filters_dto: InOrganizationFiltersDTO
    ) -> OutOrganizationPaginationDTO:
        try:
            limit = filters_dto.limit
            offset = filters_dto.offset

            order_expr = Organization._get_order_expression(filters_dto.order_by_field, filters_dto.direction_order)
            filters = Organization._get_filters(filters_dto)

            base_query = (
                select(Organization)
                .join(Point, Organization.point_id == Point.id)
                .options(selectinload(Organization.point), selectinload(Organization.activities))
                .where(*filters)
            )

            total_count_stmt = select(func.count()).select_from(base_query.subquery())
            total_count = await session.scalar(total_count_stmt) or 0

            stmt = base_query.order_by(order_expr).limit(limit).offset(offset)

            result = await session.execute(stmt)
            rows = result.scalars().unique().all()

            return OutOrganizationPaginationDTO(limit=limit, offset=offset, total=total_count, data=rows)
        except SQLAlchemyError as exc:
            logger.error("Error getting organization pagination", exc_info=exc)
            raise OrganizationPaginException from exc

    @staticmethod
    def _get_order_expression(field: OrderByOrganization, direction: OrderByType):
        mapping = {
            OrderByOrganization.CREATED_AT: Organization.created_at,
            OrderByOrganization.UPDATED_AT: Organization.updated_at,
            OrderByOrganization.NAME: Organization.name,
        }

        column = mapping[field]

        if direction == OrderByType.DESC:
            return column.desc()
        return column.asc()

    @staticmethod
    def _get_filters(filters_dto: InOrganizationFiltersDTO) -> list:
        filters = []

        if filters_dto.activity:
            filters.append(Organization.activity_ids.overlap(filters_dto.activity))

        if filters_dto.point_id:
            filters.append(Organization.point_id == filters_dto.point_id)
        if filters_dto.name:
            filters.append(Organization.name.ilike(f"%{filters_dto.name}%"))
        if filters_dto.like_address:
            filters.append(Point.address.ilike(f"%{filters_dto.like_address}%"))
        if filters_dto.lat is not None and filters_dto.lon is not None and filters_dto.radius_m is not None:
            point = from_shape(ShapelyPoint(filters_dto.lon, filters_dto.lat), srid=4326)
            filters.append(func.ST_DistanceSphere(Point.location, point) <= filters_dto.radius_m)
        return filters
