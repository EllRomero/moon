from functools import partial
from uuid import UUID

from fastapi import APIRouter, Depends
from inject import instance

from schemas.dto.input.activity import InActivityDTO, InUpdateActivityDTO
from service.activity import ActivitiesService


activity_router = APIRouter(prefix="/api/activities", tags=["ACTIVITY"])


@activity_router.post("")
async def create_activity(
    data: InActivityDTO,
    activity_service: ActivitiesService = Depends(partial(instance, ActivitiesService)),
):
    new_data = await activity_service.create_activity(data)
    return new_data


@activity_router.patch("")
async def update_activity(
    data: InUpdateActivityDTO,
    activity_service: ActivitiesService = Depends(partial(instance, ActivitiesService)),
):
    await activity_service.update_activity(data)
    return {"status": True}


@activity_router.get("/{act_id:uuid}")
async def get_activity(
    act_id: UUID,
    activity_service: ActivitiesService = Depends(partial(instance, ActivitiesService)),
):
    data = await activity_service.get_activity_by_id(act_id)
    return data


@activity_router.delete("/{act_id:uuid}")
async def delete_activity(
    act_id: UUID,
    activity_service: ActivitiesService = Depends(partial(instance, ActivitiesService)),
):
    await activity_service.delete_activity(act_id)
    return {"status": True}


@activity_router.get("")
async def get_activities(
    activity_service: ActivitiesService = Depends(partial(instance, ActivitiesService)),
):
    data = await activity_service.get_all_activities()
    return data
