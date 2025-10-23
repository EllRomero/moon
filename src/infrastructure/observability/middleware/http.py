from uuid import uuid4

import sentry_sdk
import structlog
from fastapi import FastAPI, Request, Response
from uvicorn.protocols.utils import get_path_with_query_string

from ..logger import add_fields_to_context_logger
from ..sentry import get_sentry_trace_id

http_logger = structlog.stdlib.get_logger("HttpResponse")


def http_response_logger(response: Response, request: Request, **kwargs):
    """Logs an HTTP response in a structured, Uvicorn-like format.

    This function recreates Uvicorn's access log style in a single-line message
    while also attaching additional structured fields for better observability.
    The log includes key request and response details such as status code,
    request method, client information, and request URL. Additional context
    can be passed via ``kwargs``.

    Args:
        response (Response): The outgoing FastAPI response object.
        request (Request): The incoming FastAPI request object.
        **kwargs: Arbitrary keyword arguments to include as extra structured
            log fields.
    """

    # https://www.structlog.org/en/stable/performance.html
    # logger link optimization
    logger = http_logger.bind()

    fields = {
        "url": str(request.url),
        "status_code": response.status_code,
        "client_ip": request.client.host,
        "client_port": request.client.port,
        "method": request.method,
    }

    if kwargs:
        other_fields = {k: v for k, v in kwargs.items()}
        fields | other_fields  # concat dicts

    short_url = get_path_with_query_string(request.scope)
    # Uvicorn-like log string
    msg = f'{fields["client_ip"]}:{fields["client_port"]} - "{fields["method"]} {short_url}" {fields["status_code"]}'

    # Recreate the Uvicorn access log format, but add all parameters as structured information
    logger.info(msg, fields=fields)


def add_http_logging_middleware(app: FastAPI, app_version: str, debug: bool):
    """
    Add lightweight HTTP logging middleware.
    - Binds a unique request_id and app_version into structlog context.
    - Logs a concise error message on unhandled exceptions (no traceback).
    - Lets Sentry middleware capture and report full traceback.
    """

    @app.middleware("http")
    async def logging_middleware(request: Request, call_next) -> Response:
        # See https://www.structlog.org/en/stable/performance.html
        # logger link optimization
        logger = http_logger.bind()

        # If the call_next raises an error, we still want to return our own 500 response,
        # so we can add headers to it (process time, request ID...)
        response = Response(status_code=500)
        # Clear context variables for this request scope
        structlog.contextvars.clear_contextvars()
        # Generate request id for this request
        request_id = str(uuid4())

        sentry_trace = get_sentry_trace_id(request)
        add_fields_to_context_logger(sentry_trace, app_version, request_id=request_id)

        try:
            response = await call_next(request)
        except Exception as exc:
            # Send full traceback to Sentry explicitly (logs stay concise)
            sentry_sdk.capture_exception(exc)

            if debug:
                # add traceback
                logger.exception("Application error: %s", exc, exc_info=True)
            else:
                logger.error("Application error: %s", exc, exc_info=False)
            # Re-raise so FastAPI/Sentry middleware and handlers can process it
            raise
        finally:
            # process time in seconds format
            # Send the response with additional headers
            http_response_logger(response, request)
            response.headers["X-Request-Id"] = request_id
            if sentry_trace:
                response.headers["X-Sentry-Trace-Id"] = sentry_trace
            return response
