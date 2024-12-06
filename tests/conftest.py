# pylint: disable=redefined-outer-name
# pylint: disable=unused-argument

from datetime import datetime
from os import environ
from types import SimpleNamespace
from typing import List
from uuid import uuid4

import pytest
from alembic.command import upgrade
from alembic.config import Config
from faker import Faker
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists, drop_database

from tests.utils import make_alembic_config

from movie_library.__main__ import get_app
from movie_library.config.utils import get_settings
from movie_library.db.connection import SessionManager
from movie_library.db.models import Movie, User, UserMovie


def run_upgrade(connection, cfg):
    cfg.attributes["connection"] = connection
    upgrade(cfg, "head")


async def run_async_upgrade(config: Config, database_uri: str):
    async_engine = create_async_engine(database_uri, echo=True)
    async with async_engine.begin() as conn:
        await conn.run_sync(run_upgrade, config)


@pytest.fixture()
def postgres() -> str:
    settings = get_settings()

    tmp_name = ".".join([uuid4().hex, "pytest"])
    settings.POSTGRES_DB = tmp_name
    environ["POSTGRES_DB"] = tmp_name

    tmp_url = settings.database_uri_sync
    if not database_exists(tmp_url):
        create_database(tmp_url)

    try:
        yield settings.database_uri
    finally:
        drop_database(tmp_url)


@pytest.fixture
def alembic_config(postgres) -> Config:
    cmd_options = SimpleNamespace(config="movie_library/db/", name="alembic", pg_url=postgres, raiseerr=False, x=None)
    return make_alembic_config(cmd_options)


@pytest.fixture
async def migrated_postgres(postgres, alembic_config: Config):
    await run_async_upgrade(alembic_config, postgres)


@pytest.fixture
async def client(migrated_postgres, manager: SessionManager = SessionManager()) -> AsyncClient:
    app = get_app()
    manager.refresh()
    yield AsyncClient(app=app, base_url="http://test")


@pytest.fixture
async def engine_async(postgres) -> AsyncEngine:
    engine = create_async_engine(postgres, future=True)
    yield engine
    await engine.dispose()


@pytest.fixture
def session_factory_async(engine_async) -> sessionmaker:
    return sessionmaker(engine_async, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
async def session(session_factory_async) -> AsyncSession:
    async with session_factory_async() as session:
        yield session


@pytest.fixture
async def users_sample(session) -> List:
    settings = get_settings()
    faker = Faker("ru-ru")

    new_users = []

    for _ in range(2):
        username = faker.user_name()
        password = faker.password(length=10)
        hashed_password = settings.PWD_CONTEXT.hash(password)
        email = faker.ascii_safe_email()
        user_id = uuid4()
        dt_created = datetime.strptime(faker.date(), "%Y-%m-%d")

        new_user = User(
            id=user_id,
            username=username,
            password=hashed_password,
            email=email,
            dt_created=dt_created,
            dt_updated=dt_created,
        )
        session.add(new_user)
        new_users.append(
            {
                "id": user_id,
                "username": username,
                "password": password,
                "email": email,
                "dt_created": dt_created,
                "dt_updated": dt_created,
            }
        )

    await session.commit()
    return new_users


@pytest.fixture
async def movies_sample(session, users_sample: list) -> list:
    faker = Faker()

    movies = []
    for _ in range(2):
        movie_id = str(uuid4())
        title = faker.word()
        description = faker.sentence()
        dt_created = datetime.strptime(faker.date(), "%Y-%m-%d")

        new_movie = Movie(
            id=movie_id,
            title=title,
            description=description,
            dt_created=dt_created,
            dt_updated=dt_created,
        )

        session.add(new_movie)
        movies.append(new_movie)
        await session.commit()

    return movies


@pytest.fixture
async def favorites_sample(session, users_sample: list, movies_sample: list) -> tuple[list, dict]:
    favorites = []

    for i in range(2):
        favorite = UserMovie(user_id=users_sample[0]["id"], movie_id=movies_sample[i].id)
        session.add(favorite)
        favorites.append(favorite)

    await session.commit()
    return favorites, users_sample[0]
