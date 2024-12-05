import datetime
from typing import List

from pydantic import UUID4
from sqlalchemy import delete, exc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from movie_library.db.models import Movie
from movie_library.schemas import Movie as MovieSchema


async def get_movie(session: AsyncSession, movie_id: UUID4) -> Movie | None:
    query = select(Movie).where(Movie.id == movie_id)
    return await session.scalar(query)


def get_movies_query() -> select:
    return select(Movie)


async def create_movie(session: AsyncSession, potential_movie: MovieSchema) -> MovieSchema | None:
    movie = Movie(**potential_movie.dict(exclude_unset=True))
    session.add(movie)
    try:
        await session.commit()
    except exc.IntegrityError:
        return None
    return movie


async def update_movie(session: AsyncSession, movie_id: UUID4, edited_movie: MovieSchema) -> (bool | None, str):
    movie = await get_movie(session, movie_id)

    if movie is None:
        return None, "Movie does not exist!"
    if movie.title != edited_movie.title:
        title_taken = (
            await session.scalar(
                select(Movie).where(Movie.title == edited_movie.title),
            )
            is not None
        )
        if title_taken:
            return False, "Title already exists."

    movie.title = edited_movie.title
    movie.description = edited_movie.description
    movie.dt_updated = datetime.datetime.now()
    await session.commit()
    return True, "OK"


async def delete_movie(session: AsyncSession, movie_id: UUID4) -> int:
    query = delete(Movie).where(Movie.id == movie_id)
    result = await session.execute(query)
    await session.commit()
    return result.rowcount
