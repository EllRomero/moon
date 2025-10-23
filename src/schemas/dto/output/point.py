from uuid import UUID

from geoalchemy2.elements import WKBElement
from geoalchemy2.shape import to_shape
from pydantic import BaseModel, ConfigDict, field_validator

from schemas.structure.geo import GeoLocation

from .common import OutputBasePagination


class OutPointDTO(BaseModel):
    id: UUID
    address: str
    location: GeoLocation

    model_config = ConfigDict(from_attributes=True)

    @field_validator("location", mode="before")
    @classmethod
    def convert_wkb_to_geolocation(cls, v):
        """
        Преобразует GeoAlchemy2 WKBElement в GeoLocation при конвертации из ORM.
        """
        if isinstance(v, WKBElement):
            point = to_shape(v)
            return GeoLocation(lat=point.y, lon=point.x)
        return v


# DTO с расстоянием
class OutFillingPointDTO(OutPointDTO):
    distance: float | None = None


class OutPaginPointDTO(OutputBasePagination):
    data: list[OutFillingPointDTO]
