from typing import Optional
from uuid import UUID, uuid4

from fastapi import Query
from pydantic import BaseModel, ConfigDict, Field, constr

from schemas.enums.order import OrderByFieldPoint, OrderByType
from schemas.structure.geo import GeoLocation

from .common import InBasePagination, InBaseUpdate


class InPointDTO(BaseModel):
    id: UUID = Field(default_factory=uuid4)

    address: constr(min_length=2, max_length=255)
    location: GeoLocation
    # exclude in swagger
    model_config = ConfigDict(
        json_schema_extra=lambda schema, _: [
            schema["properties"].pop("id", None),
        ]
    )


class InUpdatePointDTO(InBaseUpdate):
    id: UUID

    address: Optional[constr(min_length=2, max_length=255)] = None
    location: Optional[GeoLocation] = None


class InPointFiltersDTO(InBasePagination):
    like_address: Optional[constr(min_length=2, max_length=255)] = Query(default=None, description="Find by address")

    lat: Optional[float] = Query(default=None, ge=-90, le=90, description="Latitude of the center of the search")
    lon: Optional[float] = Query(default=None, ge=-180, le=180, description="Longitude of the center of the search")
    radius_m: Optional[int] = Query(default=None, ge=1, le=100000, description="Search radius (in meters)")

    direction_order: OrderByType = Query(default=OrderByType.DESC)
    order_by_field: OrderByFieldPoint = Query(default=OrderByFieldPoint.CREATED_AT)
