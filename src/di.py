import inject
from sqlalchemy.ext.asyncio import AsyncEngine

from di_data import DIData
from infrastructure.repositories.unit_of_work import UnitOfWork
from service.organization import OrganizationsService
from settings import Settings
from utils.systemz import SystemZ


def config_di(binder: inject.Binder, di: DIData) -> None:
    # one instance for project
    binder.bind(Settings, di.setting)

    binder.bind(AsyncEngine, di.pg_engine)

    # _______________________________________________

    # the service will be create new instance for each DI call
    binder.bind_to_provider(SystemZ, lambda: SystemZ(di.pg_engine))
    binder.bind_to_provider(UnitOfWork, lambda: UnitOfWork(di.pg_engine))

    binder.bind_to_provider(OrganizationsService, lambda: OrganizationsService())
