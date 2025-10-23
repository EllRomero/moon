import enum


class ErrorType(enum.Enum):
    NO_TYPE = ""

    UNKNOWN_EXCEPTION = "UnknownErrorException"

    ORGANIZATION_CREATE_EXCEPTION = "OrganizationCreateException"
    ORGANIZATION_DELETE_EXCEPTION = "OrganizationDeleteException"
    ORGANIZATION_UPDATE_EXCEPTION = "OrganizationUpdateException"
    ORGANIZATION_GET_EXCEPTION = "OrganizationGetException"
    ORGANIZATION_PAGIN_EXCEPTION = "OrganizationPaginException"
    ORGANIZATION_ALREADY_EXISTS_EXCEPTION = "OrganizationAlreadyExistsException"
    ORGANIZATION_NOT_EXIST_EXCEPTION = "OrganizationNotExistException"

    POINT_CREATE_EXCEPTION = "PointCreateException"
    POINT_GET_BY_ID_EXCEPTION = "PointGetByIdException"
    POINT_PAGIN_EXCEPTION = "PointPaginException"
    POINT_UPDATE_EXCEPTION = "PointUpdateException"
    POINT_DELETE_EXCEPTION = "PointDeleteException"
    POINT_ALREADY_EXISTS_EXCEPTION = "PointAlreadyExistsException"

    ACTIVITY_CREATE_EXCEPTION = "ActivityCreateException"
    ACTIVITY_DELETE_EXCEPTION = "ActivityDeleteException"
    ACTIVITY_UPDATE_EXCEPTION = "ActivityUpdateException"
    ACTIVITY_GET_EXCEPTION = "ActivityGetException"
    ACTIVITY_NOT_EXIST_EXCEPTION = "ActivityNotExistException"


class ErrorMessage(enum.Enum):
    NO_MESSAGE = ""

    UNKNOWN_EXCEPTION = "UnknownErrorException"

    ORGANIZATION_CREATE_EXCEPTION = "Organization already exists"
    ORGANIZATION_DELETE_EXCEPTION = "An error occurred while deleting the organization"
    ORGANIZATION_UPDATE_EXCEPTION = "An error occurred while updating the organization"
    ORGANIZATION_GET_EXCEPTION = "An error occurred while getting the organization"
    ORGANIZATION_PAGIN_EXCEPTION = "An error occurred while getting the organization"
    ORGANIZATION_ALREADY_EXISTS_EXCEPTION = "Organization already exists"
    ORGANIZATION_NOT_EXIST_EXCEPTION = "Organization not exist"

    POINT_CREATE_EXCEPTION = "an error occurred when creating the point"
    POINT_GET_BY_ID_EXCEPTION = "an error occurred when getting the point by id"
    POINT_PAGIN_EXCEPTION = "an error occurred when getting with pagination the point"
    POINT_UPDATE_EXCEPTION = "an error occurred when updating the point"
    POINT_DELETE_EXCEPTION = "an error occurred when deleting the point"
    POINT_ALREADY_EXISTS_EXCEPTION = "the point already exists this id or address"

    ACTIVITY_CREATE_EXCEPTION = "Activity already exists"
    ACTIVITY_DELETE_EXCEPTION = "An error occurred while deleting the activity"
    ACTIVITY_UPDATE_EXCEPTION = "An error occurred while updating the activity"
    ACTIVITY_GET_EXCEPTION = "An error occurred while getting the activity"
    ACTIVITY_NOT_EXIST_EXCEPTION = "Activity not exist"
