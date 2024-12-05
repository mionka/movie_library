import datetime

from pydantic import UUID4
from sqlalchemy import and_, delete, exc, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from movie_library.db.models import Movie, User, UserMovie
from movie_library.schemas import Movie as MovieSchema
from movie_library.schemas import User as UserSchema
from movie_library.utils.movie import get_movie


async def add_favorite(session: AsyncSession, user: User, movie_id: UUID4) -> bool | None:
    movie = await get_movie(session, movie_id)
    if movie is None:
        return None

    query = select(UserMovie).where(and_(UserMovie.user_id == user.id, UserMovie.movie_id == movie_id))
    favorite = await session.scalar(query)

    print("lala", favorite)
    if favorite is not None:
        return False

    session.add(
        UserMovie(
            user_id=user.id,
            movie_id=movie.id,
        )
    )
    await session.commit()
    return True


async def delete_favorite(session: AsyncSession, user: User, movie_id: UUID4) -> int:
    query = delete(UserMovie).where(and_(UserMovie.user_id == user.id, UserMovie.movie_id == movie_id))
    result = await session.execute(query)
    await session.commit()
    return result.rowcount


async def get_favorites_query(session: AsyncSession, user: User) -> select:
    return select(Movie).join(UserMovie).where(UserMovie.user_id == user.id)
