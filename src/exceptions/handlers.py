from fastapi.responses import ORJSONResponse


async def general_exception_handler(request, exception) -> ORJSONResponse:  # pylint: disable=W0613
    return ORJSONResponse(
        status_code=exception.status_code,
        content={"error_type": exception.error_type, "error_msg": exception.error_msg},
    )


async def unprocessable_entity_422_handler(request, exception) -> ORJSONResponse:  # pylint: disable=W0613
    return ORJSONResponse(
        status_code=exception.status_code,
        content={
            "detail": [
                {
                    "loc": [],
                    "error_msg": exception.error_msg,
                    "error_type": exception.error_type,
                }
            ]
        },
    )


handlers = {}
