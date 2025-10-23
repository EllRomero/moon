from typing import Optional
from uuid import UUID, uuid4

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field, constr

from schemas.enums.order import OrderByOrganization, OrderByType

from .common import InBasePagination, InBaseUpdate


class InOrganizationDTO(BaseModel):
    id: UUID = Field(default_factory=uuid4)

    name: constr(max_length=255, pattern=r"^[\w\s\-\.\,\(\)а-яА-ЯёЁ]+$")
    phone_number: constr(
        pattern="^((\+8|\+7)[\- ]?)?\(?\d{3,5}\)?[\- ]?\d{1}[\- ]?\d{1}[\- ]?\d{1}[\- ]?\d{1}[\- ]?\d{1}(([\- ]?\d{1})?[\- ]?\d{1})?$"
    )  # type: ignore  # noqa: S930
    point_id: UUID
    activity_ids: list[UUID]

    # exclude in swagger
    model_config = ConfigDict(
        json_schema_extra=lambda schema, _: [
            schema["properties"].pop("id", None),
        ]
    )


class InOrganizationUpdateDTO(InBaseUpdate):
    id: UUID
    phone_number: Optional[
        constr(
            pattern="^((\+8|\+7)[\- ]?)?\(?\d{3,5}\)?[\- ]?\d{1}[\- ]?\d{1}[\- ]?\d{1}[\- ]?\d{1}[\- ]?\d{1}(([\- ]?\d{1})?[\- ]?\d{1})?$"
        )
    ] = None  # type: ignore  # noqa: S930
    point_id: Optional[UUID] = None
    type_of_activity_id: Optional[UUID] = None


class InOrganizationFiltersDTO(InBasePagination):
    name: Optional[str] = Query(default=None, description="Search by organization name")
    activity: Optional[list[UUID]] = Query(default=None, description="List of activity UUIDs to filter by")

    like_address: Optional[constr(min_length=2, max_length=255)] = Query(default=None, description="Find by address")

    point_id: Optional[UUID] = Query(default=None)
    #  OR search by geo
    lat: Optional[float] = Query(default=None, ge=-90, le=90, description="Latitude of the center of the search")
    lon: Optional[float] = Query(default=None, ge=-180, le=180, description="Longitude of the center of the search")
    radius_m: Optional[int] = Query(default=None, ge=1, le=100000, description="Search radius (in meters)")

    direction_order: OrderByType = Query(default=OrderByType.DESC)
    order_by_field: OrderByOrganization = Query(default=OrderByOrganization.CREATED_AT)
