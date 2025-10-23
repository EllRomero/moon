from functools import partial
from uuid import UUID

from fastapi import APIRouter, Depends
from inject import instance

from schemas.dto.input.organization import InOrganizationDTO, InOrganizationFiltersDTO, InOrganizationUpdateDTO
from service.organization import OrganizationsService

organization_router = APIRouter(prefix="/api/organizations", tags=["ORGANIZATION"])


@organization_router.post("")
async def create_organizations(
    data: list[InOrganizationDTO],
    organization_service: OrganizationsService = Depends(partial(instance, OrganizationsService)),
):
    new_data = await organization_service.create_organizations(data)
    return new_data


@organization_router.patch("")
async def update_organization(
    data: InOrganizationUpdateDTO,
    organization_service: OrganizationsService = Depends(partial(instance, OrganizationsService)),
):
    await organization_service.update_organization(data)
    return {"status": True}


@organization_router.get("/{org_id:uuid}")
async def get_organization(
    org_id: UUID,
    organization_service: OrganizationsService = Depends(partial(instance, OrganizationsService)),
):
    data = await organization_service.get_organization_by_id(org_id)
    return data


@organization_router.delete("/{org_id:uuid}")
async def delete_organization(
    org_id: UUID,
    organization_service: OrganizationsService = Depends(partial(instance, OrganizationsService)),
):
    await organization_service.delete_organization(org_id)
    return {"status": True}


@organization_router.get("/paginate")
async def get_organizations_with_pagination(
    filters: InOrganizationFiltersDTO = Depends(),
    organization_service: OrganizationsService = Depends(partial(instance, OrganizationsService)),
):
    data = await organization_service.get_organizations_with_pagination(filters)
    return data
