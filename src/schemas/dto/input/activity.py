from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, constr

from .common import InBaseUpdate


class InActivityDTO(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: constr(max_length=255, pattern=r"^[\w\s\-\.\,\(\)а-яА-ЯёЁ]+$")
    parent_id: Optional[UUID]
    depth_level: Optional[int]

    # exclude in swagger
    model_config = ConfigDict(
        json_schema_extra=lambda schema, _: [
            schema["properties"].pop("id", None),
        ]
    )


class InUpdateActivityDTO(InBaseUpdate):
    id: UUID
    name: constr(max_length=255, pattern=r"^[\w\s\-\.\,\(\)а-яА-ЯёЁ]+$")
    parent_id: Optional[UUID]
    depth_level: Optional[int]
