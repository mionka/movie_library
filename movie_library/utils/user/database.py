import datetime

from pydantic import UUID4
from sqlalchemy import delete, exc, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from movie_library.db.models import User
from movie_library.schemas import RegistrationForm, UserEdit


async def get_user(session: AsyncSession, username: str) -> User | None:
    query = select(User).where(User.username == username)
    return await session.scalar(query)


async def register_user(session: AsyncSession, potential_user: RegistrationForm) -> tuple[bool, str]:
    user = User(**potential_user.dict(exclude_unset=True))
    session.add(user)
    try:
        await session.commit()
    except exc.IntegrityError:
        return False, "Username or email already exists."
    return True, "Successful registration!"


async def update_user(session: AsyncSession, user: User, edited_user: UserEdit) -> tuple[bool, str]:
    if user.username != edited_user.username:
        username_taken = await get_user(session, edited_user.username) is not None
        if username_taken:
            return False, "Username already exists."

    if user.email != edited_user.email:
        email_taken = (
            await session.scalar(
                select(User).where(User.email == edited_user.email),
            )
            is not None
        )
        if email_taken:
            return False, "Email is taken."

    user.username = edited_user.username
    user.password = edited_user.password if edited_user.password is not None else user.password
    user.email = edited_user.email
    user.dt_updated = datetime.datetime.now()
    await session.commit()
    return True, "OK"


async def delete_user(session: AsyncSession, user: User) -> int:
    query = delete(User).where(User.username == user.username)
    result = await session.execute(query)
    await session.commit()
    return result.rowcount
