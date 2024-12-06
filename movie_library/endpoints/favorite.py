from fastapi import APIRouter, Depends, HTTPException, Path, Request, Response
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from movie_library.db.connection import get_session
from movie_library.db.models import User
from movie_library.schemas import MovieResponse
from movie_library.utils.favorite import add_favorite, delete_favorite, get_favorites_query
from movie_library.utils.user import get_current_user


api_router = APIRouter(
    prefix="/favorite",
    tags=["Favorite"],
)


@api_router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=Page[MovieResponse],
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Could not validate credentials.",
        },
    },
)
async def get_favorites(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    query = await get_favorites_query(session, current_user)
    if query is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials.")
    return await paginate(session, query)


@api_router.post(
    "/{movie_id}",
    status_code=status.HTTP_201_CREATED,
    response_class=Response,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Bad parameters for favorite.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Could not validate credentials.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Film does not exist.",
        },
    },
)
async def create_favorite(
    _: Request,
    movie_id: str = Path(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    is_created = await add_favorite(session, current_user, movie_id)
    if is_created is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found!",
        )
    if not is_created:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Movie is already in favorites!",
        )


@api_router.delete(
    "/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Could not validate credentials.",
        },
    },
)
async def del_favorite(
    movie_id: UUID4 = Path(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await delete_favorite(session, current_user, movie_id)
