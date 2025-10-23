from pydantic import BaseModel


class OutputBasePagination(BaseModel):
    total: int
    offset: int
    limit: int
