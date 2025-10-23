from functools import partial

from fastapi import APIRouter, Depends, HTTPException
from inject import instance
from structlog import get_logger

from utils.systemz import SystemZ

logger = get_logger("SystemZ")
system_router = APIRouter(prefix="/system", tags=["SYSTEM"])


@system_router.get("/healthz")
async def healthz(systemz: SystemZ = Depends(partial(instance, SystemZ))):
    """
    Verification of status system.
    The function checks all nodes on which it depends,
    and if any of the nodes is unavailable, it displays a 409 error,
    as well as details of the incident that occurred.

    Parameters:
    None
    """
    try:
        await systemz.ping_pg()
        return {"status": True}
    except Exception as exc:
        logger.exc(str(exc))
        raise HTTPException(status_code=409, detail=str(exc))


@system_router.get("/readyz")
async def readyz():
    return {"status": True}
