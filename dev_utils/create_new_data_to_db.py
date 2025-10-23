"""
!! run this file call from workspace
"""

import asyncio
import pathlib
import argparse
import random
import sys
import re
from uuid import UUID
from collections import defaultdict

import inject
from faker import Faker

# current path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from structlog import get_logger

from di_data import make_di_data
from main import _make_lifespan
from settings import Settings
from service.point import PointService
from service.activity import ActivitiesService
from service.organization import OrganizationsService
from schemas.dto.input.point import InPointDTO
from schemas.dto.input.activity import InActivityDTO
from schemas.dto.input.organization import InOrganizationDTO


logger = get_logger("faker_logger")

fake = Faker("ru_RU")


def _fake_russian_phone() -> str:
    code = random.randint(900, 999)
    return f"+7 ({code}) {random.randint(100,999)}-{random.randint(10,99)}-{random.randint(10,99)}"


def generate_organizations(
    generate_count: int,
    points: list["InPointDTO"],
    activities: list["InActivityDTO"],
) -> list["InOrganizationDTO"]:
    orgs: list[InOrganizationDTO] = []

    for _ in range(generate_count):
        point = random.choice(points)
        name = fake.company()
        clean_name = re.sub(r"[^\w\s\-\.\,\(\)а-яА-ЯёЁ]", "", name)
        selected_activities = (
            [a.id for a in random.sample(activities, k=random.randint(1, min(3, len(activities))))]
            if activities else []
        )

        org = InOrganizationDTO(
            name=clean_name,
            phone_number=_fake_russian_phone(),
            point_id=point.id,
            activity_ids=selected_activities,
        )
        orgs.append(org)

    return orgs


def generate_points(generate_count: int) -> list["InPointDTO"]:
    points: list[InPointDTO] = []

    for _ in range(generate_count):
        lat = fake.latitude()
        lon = fake.longitude()
        location = {"lat": lat, "lon": lon}

        point = InPointDTO(
            address=fake.address(),
            location=location,
        )
        points.append(point)

    return points


def generate_activities(generate_count: int) -> list[InActivityDTO]:
    activities: list[InActivityDTO] = []
    id_map: dict[int, list[UUID]] = defaultdict(list)

    for _ in range(generate_count):
        depth_level = 1
        parent_id = None

        possible_depths = [lvl for lvl in (1, 2) if id_map[lvl]]
        if possible_depths:
            parent_depth = random.choice(possible_depths)
            parent_id = random.choice(id_map[parent_depth])
            depth_level = parent_depth + 1

        activity = InActivityDTO(
            name=fake.word(),
            parent_id=parent_id,
            depth_level=depth_level,
        )
        activities.append(activity)
        id_map[depth_level].append(activity.id)

    return activities


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Init dev data")
    parser.add_argument("-count", action="store", dest="count", help="Count of instances to create", default=1, type=int)
    args = parser.parse_args()
    return args


@inject.autoparams()
async def seed(
    src_organization: OrganizationsService,
    src_activity: ActivitiesService,
    src_point: PointService
):
    args = _parse_args()
    activities = generate_activities(args.count)
    points = generate_points(args.count)
    orgs = generate_organizations(args.count, points, activities)
    await src_point.create_point(points)
    logger.info("Points was successfully created")
    await src_activity.create_activity(activities)
    logger.info("Activities was successfully created")
    await src_organization.create_organizations(orgs)
    logger.info("Organizations was successfully created")


async def main():
    logger.info("start seed...")
    settings = Settings()
    logger.info("init DI data...")
    didata = make_di_data(setting=settings)
    lifespan = _make_lifespan(didata)

    async with lifespan(None):
        await seed()
    logger.info("done")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
