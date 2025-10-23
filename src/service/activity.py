from logging import getLogger
from uuid import UUID

import inject

from infrastructure.repositories.unit_of_work import UnitOfWork
from schemas.dto.input.activity import InActivityDTO, InUpdateActivityDTO
from schemas.dto.output.activity import OutActivityDTO


logger = getLogger(__name__)


class ActivitiesService:
    @inject.autoparams()
    def __init__(
        self,
        uow: UnitOfWork,
    ):
        self.uow = uow

    async def create_activity(self, data: list[InActivityDTO]) -> list[UUID]:
        async with self.uow as uow:
            await uow.activities.create(data)

    async def get_activity_by_id(self, org_id: UUID) -> OutActivityDTO | None:
        async with self.uow as uow:
            return await uow.activities.get_by_id(org_id)

    async def update_activity(self, updated_data: InUpdateActivityDTO) -> None:
        async with self.uow as uow:
            await uow.activities.update(updated_data.id, updated_data)

    async def delete_activity(self, org_id: UUID) -> None:
        async with self.uow as uow:
            await uow.activities.delete(org_id)

    async def get_all_activities(self) -> list[OutActivityDTO]:
        async with self.uow as uow:
            return await uow.activities.get_all()
