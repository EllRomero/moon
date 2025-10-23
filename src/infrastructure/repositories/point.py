from uuid import UUID

from geoalchemy2 import WKTElement
from structlog import get_logger

from exceptions.exc import (
    PointCreateException,
    PointDeleteException,
    PointUpdateException,
)
from infrastructure.repositories.db_models.point import Point
from schemas.dto.input.point import InPointDTO, InPointFiltersDTO, InUpdatePointDTO
from schemas.dto.output.point import OutPaginPointDTO

from .base import BaseRepository

logger = get_logger("PointRepository")


class PointRepository(BaseRepository):
    async def create(self, data: list[InPointDTO]):
        validate_data = [
            {
                "id": obj.id,
                "address": obj.address,
                "location": WKTElement(f"POINT({obj.location.lon} {obj.location.lat})", srid=4326),
            }
            for obj in data
        ]
        success = await Point.create(self.session, validate_data)
        if not success:
            msg = "Error point not created"
            logger.warning(msg)
            raise PointCreateException

    async def get_with_pagination(self, filters_dto: InPointFiltersDTO) -> OutPaginPointDTO:
        data = await Point.get_with_pagination(self.session, filters_dto)
        return data

    async def update(self, point_id: UUID, data: InUpdatePointDTO):
        data = data.model_dump(exclude_none=True, exclude={"id"})
        success = await Point.update(self.session, point_id, data)
        if not success:
            msg = f"Point {point_id} was not updated"
            logger.warning(msg)
            raise PointUpdateException

    async def delete(self, point_id: UUID):
        success = await Point.delete(self.session, point_id)
        if not success:
            msg = f"Point {point_id} was not deleted"
            logger.warning(msg)
            raise PointDeleteException
