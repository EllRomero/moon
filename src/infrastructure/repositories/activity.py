from uuid import UUID

from structlog import get_logger

from exceptions.exc import (
    ActivityCreateException,
    ActivityGetException,
    ActivityNotExistsException,
    ActivityUpdateException,
)
from infrastructure.repositories.db_models.activity import Activity
from schemas.dto.input.activity import InActivityDTO, InUpdateActivityDTO
from schemas.dto.output.activity import OutActivityDTO

from .base import BaseRepository


logger = get_logger("ActivityRepository")


class ActivityRepository(BaseRepository):
    async def create(self, data: list[InActivityDTO]) -> None:
        validate_data = [obj.model_dump(exclude_none=True) for obj in data]
        success = await Activity.create(self.session, validate_data)
        if not success:
            msg = "Error, activity not created"
            logger.warning(msg)
            raise ActivityCreateException

    async def get_by_id(self, activity_id: UUID) -> OutActivityDTO | None:
        data = await Activity.get_by_id(self.session, activity_id)
        if not data:
            logger.error(f"Activity {activity_id} not found")
            raise ActivityGetException
        return data

    async def update(self, data: InUpdateActivityDTO):
        activity_data = data.model_dump()
        activity_id = activity_data.pop("id")
        success = await Activity.update(self.session, activity_id, activity_data)
        if not success:
            msg = f"Activity {activity_id} was not updated"
            logger.warning(msg)
            raise ActivityUpdateException

    async def delete(self, activity_id: UUID):
        success = await Activity.delete(self.session, activity_id)
        if not success:
            msg = f"Activity {activity_id} was not deleted"
            logger.warning(msg)
            raise ActivityNotExistsException

    async def get_all(self) -> list[OutActivityDTO]:
        success = await Activity.get_all()
        if not success:
            msg = "Activities was not found"
            logger.warning(msg)
            raise ActivityNotExistsException
