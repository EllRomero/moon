import asyncio
from contextlib import asynccontextmanager
from functools import partial

import inject
import uvicorn
import uvloop
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse
from structlog import get_logger

from di import config_di
from di_data import make_di_data
from exceptions.handlers import handlers
from routes.config import include_routes
from settings import Settings

logger = get_logger(__name__)


def _make_lifespan(didata):
    @asynccontextmanager
    async def lifespan(app: FastAPI):  # pylint: disable=unused-argument
        _config_di = partial(config_di, di=didata)
        inject.clear_and_configure(_config_di)

        yield

        inject.clear()

    return lifespan


def _create_app(settings: Settings) -> FastAPI:
    didata = make_di_data(setting=settings)

    app = FastAPI(
        title=settings.app.PROJECT_NAME,
        docs_url=settings.app.DOCS_URL,
        openapi_url=settings.app.OPENAPI_URL,
        exception_handlers=handlers,
        lifespan=_make_lifespan(didata),
        default_response_class=ORJSONResponse,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=settings.app.CORS_ORIGINS_REGEX,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    include_routes(app)
    # module for example of observability to test task
    # init_observability(settings, app)
    return app


async def run_server(settings: Settings) -> None:
    uvicorn_config = uvicorn.Config(
        app=_create_app(settings),
        host=settings.app.SERVER_HOST,
        port=settings.app.SERVER_PORT,
        log_level=settings.logger.LOG_LEVEL.lower(),
        timeout_keep_alive=20,
    )
    srv = uvicorn.Server(config=uvicorn_config)
    logger.info("Server is running")
    try:
        await srv.serve()
    except Exception:  # pylint: disable=broad-except
        await srv.shutdown()


def setup_event_loop(settings: Settings) -> asyncio.AbstractEventLoop:
    uvloop.install()
    loop_loc = asyncio.get_event_loop()
    loop_loc.set_debug(settings.app.DEBUG)
    return loop_loc


async def main(settings: Settings) -> None:
    await run_server(settings)


if __name__ == "__main__":
    try:
        settings = Settings()
        loop = setup_event_loop(settings)
        loop.run_until_complete(main(settings))
    except KeyboardInterrupt:
        logger.info("Stopped by user (CTRL+C)")
