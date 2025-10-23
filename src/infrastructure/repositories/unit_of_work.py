import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio.session import async_sessionmaker

from .activity import ActivityRepository
from .organization import OrganizationRepository
from .point import PointRepository

logger = logging.getLogger(__name__)


class UnitOfWork:
    def __init__(self, db: AsyncEngine) -> None:
        self._session_maker = async_sessionmaker(db, expire_on_commit=False, class_=AsyncSession)
        self.session: Optional[AsyncSession] = None
        self._init_available_repositories()

    def _init_available_repositories(self):
        # when calling property,
        # the available repositories will be initialized.
        self._organizations = None
        self._activities = None
        self._points = None

    def _clear_repositories(self):
        self._organizations = None
        self._activities = None
        self._points = None

    async def __aenter__(self) -> "UnitOfWork":
        self.session = self._session_maker()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                await self.session.commit()
            else:
                await self.session.rollback()
        except Exception as ex:
            logger.error(str(ex))
            await self.session.rollback()
            raise
        finally:
            await self.session.close()
            self.session = None
            self._clear_repositories()

    @property
    def organizations(self) -> OrganizationRepository:
        if not self._organizations:
            self._organizations = OrganizationRepository(self.session)
        return self._organizations

    @property
    def activities(self) -> ActivityRepository:
        if not self._activities:
            self._activities = ActivityRepository(self.session)
        return self._activities

    @property
    def points(self) -> PointRepository:
        if not self._points:
            self._points = PointRepository(self.session)
        return self._points
