from enum import StrEnum


class OrderByType(StrEnum):
    ASC = "asc"
    DESC = "desc"


class OrderByOrganization(StrEnum):
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    NAME = "name"


class OrderByFieldPoint(StrEnum):
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
    DISTANCE = "distance"
