from fastapi import status

from exceptions.enums import ErrorMessage, ErrorType
from exceptions.handlers import general_exception_handler, handlers


class CustomException(Exception):
    error_type: ErrorType = ErrorType.NO_TYPE
    error_msg: ErrorMessage = ErrorMessage.NO_MESSAGE
    status_code: int = status.HTTP_400_BAD_REQUEST

    # can be overridden to use a different handler for its error
    handler = general_exception_handler

    def __init_subclass__(cls, **kwargs):
        """Automatically registers the exception subclass with its handler.

        This method is called when a subclass of `CustomException` is defined.
        It ensures that the subclass is associated with its error handler in the
        global `handlers` registry, allowing custom exception handling behavior.

        If the subclass defines its own `handler` attribute, that handler will be
        registered instead of the default `general_exception_handler`.

        Args:
            **kwargs: Arbitrary keyword arguments passed to the superclass.

        """
        super().__init_subclass__(**kwargs)
        if cls.handler:
            handlers[cls] = cls.handler


class UnknownErrorException(CustomException):
    error_type = ErrorType.UNKNOWN_EXCEPTION
    error_msg = ErrorMessage.UNKNOWN_EXCEPTION
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


class OrganizationCreateException(CustomException):
    error_type = ErrorType.ORGANIZATION_CREATE_EXCEPTION
    error_msg = ErrorMessage.ORGANIZATION_CREATE_EXCEPTION
    status_code = status.HTTP_400_BAD_REQUEST


class OrganizationUpdateException(CustomException):
    error_type = ErrorType.ORGANIZATION_UPDATE_EXCEPTION
    error_msg = ErrorMessage.ORGANIZATION_UPDATE_EXCEPTION
    status_code = status.HTTP_400_BAD_REQUEST


class OrganizationDeleteException(CustomException):
    error_type = ErrorType.ORGANIZATION_DELETE_EXCEPTION
    error_msg = ErrorMessage.ORGANIZATION_DELETE_EXCEPTION
    status_code = status.HTTP_400_BAD_REQUEST


class OrganizationNotExistsException(CustomException):
    error_type = ErrorType.ORGANIZATION_NOT_EXIST_EXCEPTION
    error_msg = ErrorMessage.ORGANIZATION_NOT_EXIST_EXCEPTION
    status_code = status.HTTP_400_BAD_REQUEST


class OrganizationGetException(CustomException):
    error_type = ErrorType.ORGANIZATION_GET_EXCEPTION
    error_msg = ErrorMessage.ORGANIZATION_GET_EXCEPTION
    status_code = status.HTTP_400_BAD_REQUEST


class OrganizationPaginException(CustomException):
    error_type = ErrorType.ORGANIZATION_PAGIN_EXCEPTION
    error_msg = ErrorMessage.ORGANIZATION_PAGIN_EXCEPTION
    status_code = status.HTTP_400_BAD_REQUEST


class OrganizationAlreadyExistsException(CustomException):
    error_type = ErrorType.ORGANIZATION_ALREADY_EXISTS_EXCEPTION
    error_msg = ErrorMessage.ORGANIZATION_ALREADY_EXISTS_EXCEPTION
    status_code = status.HTTP_400_BAD_REQUEST


class PointCreateException(CustomException):
    error_type = ErrorType.POINT_CREATE_EXCEPTION
    error_msg = ErrorMessage.POINT_CREATE_EXCEPTION
    status_code = status.HTTP_409_CONFLICT


class PointGetByIdException(CustomException):
    error_type = ErrorType.POINT_GET_BY_ID_EXCEPTION
    error_msg = ErrorMessage.POINT_GET_BY_ID_EXCEPTION
    status_code = status.HTTP_404_NOT_FOUND


class PointUpdateException(CustomException):
    error_type = ErrorType.POINT_UPDATE_EXCEPTION
    error_msg = ErrorMessage.POINT_UPDATE_EXCEPTION
    status_code = status.HTTP_409_CONFLICT


class PointDeleteException(CustomException):
    error_type = ErrorType.POINT_DELETE_EXCEPTION
    error_msg = ErrorMessage.POINT_DELETE_EXCEPTION
    status_code = status.HTTP_409_CONFLICT


class PointPaginException(CustomException):
    error_type = ErrorType.POINT_PAGIN_EXCEPTION
    error_msg = ErrorMessage.POINT_PAGIN_EXCEPTION
    status_code = status.HTTP_404_NOT_FOUND


class PointAlreadyExistsException(CustomException):
    error_type = ErrorType.POINT_ALREADY_EXISTS_EXCEPTION
    error_msg = ErrorMessage.POINT_ALREADY_EXISTS_EXCEPTION
    status_code = status.HTTP_409_CONFLICT

class ActivityCreateException(CustomException):
    error_type = ErrorType.ACTIVITY_CREATE_EXCEPTION
    error_msg = ErrorMessage.ACTIVITY_CREATE_EXCEPTION
    status_code = status.HTTP_400_BAD_REQUEST


class ActivityUpdateException(CustomException):
    error_type = ErrorType.ACTIVITY_UPDATE_EXCEPTION
    error_msg = ErrorMessage.ACTIVITY_UPDATE_EXCEPTION
    status_code = status.HTTP_400_BAD_REQUEST


class ActivityDeleteException(CustomException):
    error_type = ErrorType.ACTIVITY_DELETE_EXCEPTION
    error_msg = ErrorMessage.ACTIVITY_DELETE_EXCEPTION
    status_code = status.HTTP_400_BAD_REQUEST


class ActivityNotExistsException(CustomException):
    error_type = ErrorType.ACTIVITY_NOT_EXIST_EXCEPTION
    error_msg = ErrorMessage.ACTIVITY_NOT_EXIST_EXCEPTION
    status_code = status.HTTP_400_BAD_REQUEST

class ActivityGetException(CustomException):
    error_type = ErrorType.ACTIVITY_GET_EXCEPTION
    error_msg = ErrorMessage.ACTIVITY_GET_EXCEPTION
    status_code = status.HTTP_400_BAD_REQUEST
