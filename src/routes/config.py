from fastapi import FastAPI

from .activity import activity_router
from .organization import organization_router
from .point import point_router
from .systemz import system_router


def get_routes():
    return [
        organization_router,
        point_router,
        activity_router,
        system_router,
    ]


def include_routes(app: FastAPI):
    routes = get_routes()
    for route in routes:
        app.include_router(route)
