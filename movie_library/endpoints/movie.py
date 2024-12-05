# pylint: disable=unused-argument
from fastapi import APIRouter, Body, Depends, HTTPException, Path, Request, Response
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from pydantic import UUID4
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from movie_library.db.connection import get_session
from movie_library.db.models import User
from movie_library.schemas import Movie as MovieSchema
from movie_library.schemas import MovieResponse
from movie_library.utils.movie import create_movie, delete_movie, get_movie, get_movies_query, update_movie
from movie_library.utils.user import get_current_user


api_router = APIRouter(
    prefix="/movie",
    tags=["Movie"],
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
async def search_movies(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    query = get_movies_query()
    return await paginate(session, query)


@api_router.get(
    "/{movie_id}",
    status_code=status.HTTP_200_OK,
    response_model=MovieResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Could not validate credentials.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Movie does not exist.",
        },
    },
)
async def search_movie(
    movie_id: UUID4 = Path(...),
    _: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    movie = await get_movie(session, movie_id)
    if movie is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Movie not found!",
        )
    return movie


@api_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=MovieResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Bad parameters for film.",
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Could not validate credentials.",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Movie does not exist.",
        },
    },
)
async def add_movie(
    _: Request,
    movie: MovieSchema = Body(...),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    new_movie = await create_movie(session, movie)
    if new_movie is not None:
        return new_movie
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Title already exists!",
    )


@api_router.put(
    "/edit/{movie_id}",
    status_code=status.HTTP_200_OK,
    response_class=Response,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Could not validate credentials,",
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Movie does not exist.",
        },
    },
)
async def edit(
    edited_movie: MovieSchema,
    movie_id: UUID4 = Path(...),
    _: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    result, message = await update_movie(session, movie_id, edited_movie)

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
        )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )


@api_router.delete(
    "/{movie_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Could not validate credentials",
        },
    },
)
async def takeout(
    movie_id: UUID4 = Path(...),
    _: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await delete_movie(session, movie_id)
