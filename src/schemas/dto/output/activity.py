from uuid import UUID

from pydantic import BaseModel, ConfigDict


class OutActivityDTO(BaseModel):
    id: UUID
    name: str
    depth_level: int

    model_config = ConfigDict(from_attributes=True)
