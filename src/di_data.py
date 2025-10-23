from dataclasses import dataclass, fields

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from settings import DatabaseConfig, Settings


@dataclass
class DIData:
    setting: Settings = None
    pg_engine: AsyncEngine = None

    def check_all_instances(self):
        for f in fields(self):
            if getattr(self, f.name) is None:
                raise ValueError(f"Field '{f.name}' is not initialized")


def make_di_data(setting: Settings) -> DIData:
    didata = DIData(setting=setting)

    make_for_pg(didata)

    didata.check_all_instances()
    return didata


def make_for_pg(di: DIData):
    settings: DatabaseConfig = di.setting.db
    pg_engine: AsyncEngine = create_async_engine(
        settings.get_pg_url(),
        future=True,
        pool_pre_ping=True,
        pool_recycle=3600,
    )

    di.pg_engine = pg_engine
