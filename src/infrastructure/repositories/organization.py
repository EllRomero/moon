from uuid import UUID

from structlog import get_logger

from exceptions.exc import (
    OrganizationCreateException,
    OrganizationGetException,
    OrganizationNotExistsException,
    OrganizationUpdateException,
)
from infrastructure.repositories.db_models.organization import Organization
from schemas.dto.input.organization import InOrganizationDTO, InOrganizationFiltersDTO, InOrganizationUpdateDTO
from schemas.dto.output.organization import OutOrganizationDTO, OutOrganizationPaginationDTO

from .base import BaseRepository

logger = get_logger("OrganizationRepository")


class OrganizationRepository(BaseRepository):
    async def create(self, data: list[InOrganizationDTO]):
        validate_data = [obj.model_dump(exclude_none=True) for obj in data]
        success = await Organization.create(self.session, validate_data)
        if not success:
            msg = "Error organization not created"
            logger.warning(msg)
            raise OrganizationCreateException

    async def get_by_id(self, org_id: UUID) -> OutOrganizationDTO:
        data = await Organization.get_by_id(self.session, org_id)
        if not data:
            logger.error(f"Organization {org_id} not found")
            raise OrganizationGetException
        return data

    async def get_with_pagination(self, filters_dto: InOrganizationFiltersDTO) -> OutOrganizationPaginationDTO:
        data = await Organization.get_with_pagination(self.session, filters_dto)
        return data

    async def update(self, org_id: UUID, data: InOrganizationUpdateDTO):
        data = data.model_dump(exclude_none=True, exclude={"id"})
        success = await Organization.update(self.session, org_id, data)
        if not success:
            msg = f"Organization {org_id} was not updated"
            logger.warning(msg)
            raise OrganizationUpdateException

    async def delete(self, org_id: UUID):
        success = await Organization.delete(self.session, org_id)
        if not success:
            msg = f"Organization {org_id} was not deleted"
            logger.warning(msg)
            raise OrganizationNotExistsException
