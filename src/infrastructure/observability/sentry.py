from typing import Optional

import inject
import sentry_sdk
from fastapi import Request
from sentry_sdk import get_traceparent

from settings import SentryConfig


@inject.autoparams()
def setup_sentry(settings: SentryConfig):
    """initializing the sentry in the project"""

    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        send_default_pii=settings.SEND_DEFAULT_PII,
        sample_rate=settings.SENTRY_SAMPLE_RATE,
        traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
        profile_session_sample_rate=settings.SENTRY_SESSION_SAMPLE_RATE,
        profile_lifecycle=settings.PROFILE_LIFECYCLE,
        enable_logs=settings.ENABLE_LOGS,
    )


def get_sentry_trace_id(request: Request) -> Optional[str]:
    """
    Extracts the Sentry trace ID from the request or Sentry SDK.

    The trace ID is a unique identifier shared across all requests within a
    distributed trace. If available, the trace ID is parsed from the `sentry-trace`
    request header. Otherwise, it falls back to retrieving the trace information
    from the Sentry SDK via ``get_traceparent()``.

    A `sentry-trace` header and func return has the following format::

        trace_id[32 chars]-span_id[16 chars]-sampled[1 char]

    Example:
        ``56ac0b3b76fe4771955b4d432681d3ae-a10aec35c280d302-1``

        - **trace_id**: unique identifier for the trace (all_trace route) (32 characters).
        - **span_id**: identifier for the specific span (for request uniq) (16 characters).
        - **sampled**: whether the trace is sampled and sent to Sentry (``1`` = yes, ``0`` = no).

    Args:
        request (Request): The incoming FastAPI request.

    Returns:
        Optional[str]: The 32-character Sentry trace ID, or ``None`` if unavailable.

    """

    trace_id = None

    trace_from_request = request.headers.get("sentry-trace")

    # trace_id = 32 char, therefore, we make a slice of 32 characters.
    if trace_from_request:
        trace_id = trace_from_request[:32]
    else:
        # get trace_id from sentry sdk
        trace_id = get_traceparent()[:32]

    return trace_id
