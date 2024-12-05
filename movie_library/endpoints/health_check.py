from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from movie_library.db.connection import get_session
from movie_library.schemas import MessageSuccess
from movie_library.utils.health_check import health_check_db


api_router = APIRouter(
    prefix="/health_check",
    tags=["Application Health"],
)


@api_router.get(
    "/ping_application",
    response_model=MessageSuccess,
    status_code=status.HTTP_200_OK,
)
async def ping_application(
    _: Request,
):
    return {"message": "Application works!"}


@api_router.get(
    "/ping_database",
    response_model=MessageSuccess,
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Database does not work."}},
)
async def ping_database(
    _: Request,
    session: AsyncSession = Depends(get_session),
):
    if await health_check_db(session):
        return {"message": "Database works!"}
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Database does not work.",
    )
