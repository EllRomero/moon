from fastapi import Query
from pydantic import BaseModel, model_validator


class InBasePagination(BaseModel):
    offset: int = Query(default=0, ge=0)
    limit: int = Query(default=10, le=100, ge=1)


class InBaseUpdate(BaseModel):
    @model_validator(mode="after")
    def validate_any(self):
        all_fields = self.model_dump()
        if not any((all_fields.values())):
            raise ValueError("At least one field must be provided")
        return self
