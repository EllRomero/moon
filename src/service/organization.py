from logging import getLogger
from uuid import UUID

import inject

from infrastructure.repositories.unit_of_work import UnitOfWork
from schemas.dto.input.organization import InOrganizationDTO, InOrganizationFiltersDTO, InOrganizationUpdateDTO
from schemas.dto.output.organization import OutOrganizationDTO, OutOrganizationPaginationDTO

logger = getLogger(__name__)


class OrganizationsService:
    @inject.autoparams()
    def __init__(
        self,
        uow: UnitOfWork,
    ):
        self.uow = uow

    async def create_organizations(self, data: list[InOrganizationDTO]) -> None:
        async with self.uow as uow:
            await uow.organizations.create(data)

    async def get_organization_by_id(self, org_id: UUID) -> OutOrganizationDTO:
        async with self.uow as uow:
            return await uow.organizations.get_by_id(org_id)

    async def get_organizations_with_pagination(
        self,
        filters: InOrganizationFiltersDTO,
    ) -> OutOrganizationPaginationDTO:
        async with self.uow as uow:
            return await uow.organizations.get_with_pagination(filters)

    async def update_organization(self, updated_data: InOrganizationUpdateDTO) -> None:
        async with self.uow as uow:
            await uow.organizations.update(updated_data.id, updated_data)

    async def delete_organization(self, org_id: UUID) -> None:
        async with self.uow as uow:
            await uow.organizations.delete(org_id)
