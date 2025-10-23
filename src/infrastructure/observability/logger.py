import logging
import sys

import sentry_sdk
import structlog
from structlog.types import EventDict, Processor


def add_fields_to_context_logger(sentry_trace: str, app_version: str, **kwargs) -> None:
    """
    Binds contextual fields to the structlog context for enriched logging.

    This function attaches key metadata such as the current Sentry trace ID
    and application version to the logging context using
    ``structlog.contextvars.bind_contextvars``. Once bound, these fields will
    automatically be included in all subsequent log records until they are
    cleared or overwritten.

    Args:
        sentry_trace (str): The unique 32-character Sentry trace ID used for
            correlating logs with distributed traces.
        app_version (str): The current version of the application.
        **kwargs: Additional key-value pairs to bind into the structured log
            context.

    Returns:
        None: This function updates the logger context in place.
    """
    structlog.contextvars.bind_contextvars(sentry_trace=sentry_trace, app_version=app_version, **kwargs)


def disable_module_logs(module):
    logger = logging.getLogger(module)
    logger.addHandler(logging.NullHandler())
    logger.propagate = False


def drop_color_message_key(_, __, event_dict: EventDict) -> EventDict:
    """
    Drop duplicated `color_message` added by Uvicorn so we don't log it twice.
    """
    event_dict.pop("color_message", None)
    return event_dict


def setup_fmt_logging(
    max_frames_traceback: int,
    log_disable_modules: str,
    json_logs: bool = False,
    log_level: str = "INFO",
):
    """
    Configure application logging with structlog.

    Design goals:
    - Keep logs concise (no Python tracebacks in console/stdout).
    - Send full tracebacks to Sentry (handled elsewhere / via middleware/excepthook).
    - Provide useful context (timestamp, level, logger name, callsite).
    - Support both human-readable console and JSON formatting.
    """

    timestamper = structlog.processors.TimeStamper(utc=True, fmt="%Y-%m-%d %H:%M:%S")

    # Minimal but useful processors shared between structlog and stdlib logging
    shared_processors: list[Processor] = [
        structlog.contextvars.merge_contextvars,  # inject request-scoped context
        structlog.stdlib.add_logger_name,  # add logger name
        structlog.stdlib.add_log_level,  # add level
        drop_color_message_key,  # drop uvicorn color message
        timestamper,  # add timestamp
        structlog.processors.CallsiteParameterAdder(
            {
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.FUNC_NAME,
                structlog.processors.CallsiteParameter.LINENO,
            }
        ),
    ]

    structlog.configure(
        processors=shared_processors
        + [
            # Prepare event dict for `ProcessorFormatter`.
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    if json_logs:
        # Compact JSON for log aggregators
        log_renderer = structlog.processors.JSONRenderer()
    else:
        # Human-friendly console; no traceback rendering here
        formatter = structlog.dev.RichTracebackFormatter(max_frames=max_frames_traceback)
        log_renderer = structlog.dev.ConsoleRenderer(exception_formatter=formatter)

    class ContextVarsInjector:
        def __call__(self, logger, name, event_dict):  # noqa: D401
            # Inject contextvars so stdlib logging also gets them values
            context = structlog.contextvars.get_contextvars()
            if context:
                event_dict.update(
                    {
                        "request_id": context.get("request_id"),
                        "sentry_trace": context.get("sentry_trace"),
                        "app_version": context.get("app_version"),
                    }
                )
            return event_dict

    formatter = structlog.stdlib.ProcessorFormatter(
        # These run ONLY on `logging` entries that do NOT originate within
        # structlog.
        foreign_pre_chain=shared_processors + [ContextVarsInjector()],
        # These run on ALL entries after the pre_chain is done.
        processors=[
            # Remove _record & _from_structlog.
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            log_renderer,
        ],
    )

    handler = logging.StreamHandler()
    # Apply our formatter to all stdlib logging records
    handler.setFormatter(formatter)
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level.upper())

    if json_logs:
        for module in log_disable_modules.split(","):
            disable_module_logs(module)

    def handle_exception(exc_type, exc_value, exc_traceback):
        """
        Global fallback for uncaught exceptions.
        - Do NOT print traceback to stdout logs.
        - Send the exception to Sentry with full traceback.
        - Keep a short error line in logs.
        """
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # Send full traceback to Sentry, but keep logs concise without traceback
        try:
            sentry_sdk.capture_exception(exc_value)
        except Exception:  # noqa: BLE001
            pass
        root_logger.error("Uncaught exception: %s", exc_value, exc_info=False)

    sys.excepthook = handle_exception
