from datetime import datetime
from typing import Optional
from uuid import UUID

from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape
from shapely.geometry import Point as ShapelyPoint
from sqlalchemy import DateTime, String, delete, func, select, update
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship
from structlog import get_logger

from exceptions.exc import (
    PointAlreadyExistsException,
    PointCreateException,
    PointDeleteException,
    PointPaginException,
    PointUpdateException,
)
from schemas.dto.input.point import InPointDTO, InPointFiltersDTO, InUpdatePointDTO
from schemas.dto.output.point import OutFillingPointDTO, OutPaginPointDTO, OutPointDTO
from schemas.enums.order import OrderByFieldPoint, OrderByType

from .base import BaseModel

logger = get_logger("PointModels")


class Point(BaseModel):
    __tablename__ = "points"

    id: Mapped[UUID] = mapped_column(pgUUID, primary_key=True)
    address: Mapped[str] = mapped_column(String, nullable=False)
    location = mapped_column(Geometry(geometry_type="POINT", srid=4326))  # srid=4326 stand for WGS84 (GPS)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    organizations: Mapped[list["Organization"]] = relationship(  # noqa: F821
        "Organization",
        back_populates="point",
        lazy="select",
        passive_deletes=True,
    )

    @staticmethod
    async def create(session: AsyncSession, data: list[InPointDTO]) -> list[OutPointDTO]:
        try:
            stmt = pg_insert(Point).values(data).returning(Point)
            result = await session.execute(stmt)
            rows = result.scalars().all()
            return rows
        except IntegrityError as exc:
            logger.warning("Point already exists", exc_info=exc)
            raise PointAlreadyExistsException from exc
        except SQLAlchemyError as exc:
            logger.error("Error creating point", exc_info=exc)
            raise PointCreateException from exc

    @staticmethod
    async def update(session: AsyncSession, point_id: UUID, data: InUpdatePointDTO) -> Optional[OutPointDTO]:
        try:
            stmt = update(Point).where(Point.id == point_id).values(data).returning(Point)
            row = (await session.execute(stmt)).scalar_one_or_none()
            return row
        except SQLAlchemyError as exc:
            logger.error(f"Error update point {point_id}", exc_info=exc)
            raise PointUpdateException from exc

    @staticmethod
    async def delete(session: AsyncSession, point_id: UUID) -> Optional[UUID]:
        try:
            stmt = delete(Point).where(Point.id == point_id).returning(Point.id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as exc:
            logger.error(f"Error delete point {point_id}", exc_info=exc)
            raise PointDeleteException from exc

    @staticmethod
    async def get_with_pagination(session: AsyncSession, filters_dto: InPointFiltersDTO) -> OutPaginPointDTO:
        try:
            limit = filters_dto.limit
            offset = filters_dto.offset

            filters = Point._get_filters(filters_dto)
            order_expr = Point._get_order_expression(filters_dto)

            total_count = await session.scalar(select(func.count(Point.id)).where(*filters)) or 0

            stmt = select(Point)
            if filters_dto.lat and filters_dto.lon:
                ref_point = from_shape(ShapelyPoint(filters_dto.lon, filters_dto.lat), srid=4326)
                stmt = stmt.add_columns(func.ST_DistanceSphere(Point.location, ref_point).label("distance"))

            stmt = stmt.where(*filters).order_by(order_expr).limit(limit).offset(offset)

            result = await session.execute(stmt)
            rows = result.mappings().all()
            data = [
                OutFillingPointDTO(
                    id=row["Point"].id,
                    address=row["Point"].address,
                    location=row["Point"].location,
                    distance=row.get("distance"),
                )
                for row in rows
            ]
            return OutPaginPointDTO(limit=limit, offset=offset, total=total_count, data=data)

        except SQLAlchemyError as exc:
            logger.error("Error getting with pagination point", exc_info=exc)
            raise PointPaginException from exc

    @staticmethod
    def _get_filters(filters_dto: InPointFiltersDTO) -> list:
        filters = []

        if filters_dto.like_address:
            filters.append(Point.address.ilike(f"%{filters_dto.like_address}%"))
        if filters_dto.lat is not None and filters_dto.lon is not None and filters_dto.radius_m is not None:
            point = from_shape(ShapelyPoint(filters_dto.lon, filters_dto.lat), srid=4326)
            filters.append(func.ST_DistanceSphere(Point.location, point) <= filters_dto.radius_m)
        return filters

    @staticmethod
    def _get_order_expression(filters_dto: InPointFiltersDTO):
        mapping = {
            OrderByFieldPoint.CREATED_AT: Point.created_at,
            OrderByFieldPoint.UPDATED_AT: Point.updated_at,
        }

        if filters_dto.order_by_field == OrderByFieldPoint.DISTANCE and filters_dto.lat and filters_dto.lon:
            ref_point = from_shape(ShapelyPoint(filters_dto.lon, filters_dto.lat), srid=4326)
            distance_expr = func.ST_DistanceSphere(Point.location, ref_point)
            return distance_expr.asc() if filters_dto.direction_order == OrderByType.ASC else distance_expr.desc()

        column = mapping.get(filters_dto.order_by_field, Point.created_at)
        return column.asc() if filters_dto.direction_order == OrderByType.ASC else column.desc()
