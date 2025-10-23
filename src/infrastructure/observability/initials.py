from fastapi import FastAPI

from settings import AppConfig, LoggerConfig, SentryConfig, Settings

from .logger import setup_fmt_logging
from .middleware.http import add_http_logging_middleware
from .middleware.sentry import add_sentry_middleware
from .opentelemetry import setup_opentelemetry
from .sentry import setup_sentry


def init_observability(settings: Settings, app: FastAPI):
    log_conf: LoggerConfig = settings.logger
    app_conf: AppConfig = settings.app
    sen_conf: SentryConfig = settings.sentry

    setup_fmt_logging(
        json_logs=not app_conf.DEBUG,
        log_level=log_conf.LOG_LEVEL,
        max_frames_traceback=log_conf.MAX_FRAMES_TRACEBACK,
        log_disable_modules=log_conf.LOG_DISABLE_MODULES,
    )

    setup_sentry(sen_conf)
    add_sentry_middleware(app)
    # The sentry middleware must be added first,
    # before registering the middleware for http responses.
    # Otherwise, sentry won't be able to register traceback.

    add_http_logging_middleware(
        app=app,
        app_version=app_conf.APP_VERSION,
        debug=app_conf.DEBUG,
    )

    setup_opentelemetry(app)
