from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .activity import OutActivityDTO
from .common import OutputBasePagination
from .point import OutPointDTO


class OutOrganizationDTO(BaseModel):
    id: UUID
    name: str
    phone_number: str
    point_id: UUID
    created_at: datetime
    updated_at: datetime

    point: Optional[OutPointDTO] = None
    activities: Optional[list[OutActivityDTO]] = None

    model_config = ConfigDict(from_attributes=True)


class OutOrganizationPaginationDTO(OutputBasePagination):
    data: list[OutOrganizationDTO]
