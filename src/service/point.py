from logging import getLogger
from uuid import UUID

import inject

from infrastructure.repositories.unit_of_work import UnitOfWork
from schemas.dto.input.point import InPointDTO, InPointFiltersDTO, InUpdatePointDTO
from schemas.dto.output.point import OutPaginPointDTO

logger = getLogger(__name__)


class PointService:
    @inject.autoparams()
    def __init__(
        self,
        uow: UnitOfWork,
    ):
        self.uow = uow

    async def create_point(self, data: list[InPointDTO]) -> None:
        async with self.uow as uow:
            await uow.points.create(data)

    async def get_points_with_pagination(
        self,
        filters: InPointFiltersDTO,
    ) -> OutPaginPointDTO:
        async with self.uow as uow:
            return await uow.points.get_with_pagination(filters)

    async def update_point(self, updated_data: InUpdatePointDTO) -> None:
        async with self.uow as uow:
            await uow.points.update(updated_data.id, updated_data)

    async def delete_point(self, point_id: UUID) -> None:
        async with self.uow as uow:
            await uow.points.delete(point_id)
