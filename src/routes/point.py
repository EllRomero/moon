from functools import partial
from uuid import UUID

from fastapi import APIRouter, Depends
from inject import instance

from schemas.dto.input.point import InPointDTO, InPointFiltersDTO, InUpdatePointDTO
from service.point import PointService

point_router = APIRouter(prefix="/api/points", tags=["POINT"])


@point_router.post("")
async def create_point(
    data: list[InPointDTO],
    point_service: PointService = Depends(partial(instance, PointService)),
):
    await point_service.create_point(data)
    return {"status": True}


@point_router.patch("")
async def update_point(
    data: InUpdatePointDTO,
    point_service: PointService = Depends(partial(instance, PointService)),
):
    await point_service.update_point(data)
    return {"status": True}


@point_router.delete("/{point_id:uuid}")
async def delete_point(
    point_id: UUID,
    point_service: PointService = Depends(partial(instance, PointService)),
):
    await point_service.delete_point(point_id)
    return {"status": True}


@point_router.get("/paginate")
async def get_points_with_pagination(
    filters: InPointFiltersDTO = Depends(),
    point_service: PointService = Depends(partial(instance, PointService)),
):
    data = await point_service.get_points_with_pagination(filters)
    return data
