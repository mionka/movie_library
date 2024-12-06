# pylint: disable=unused-argument

from uuid import uuid4

import pytest

from movie_library.schemas import Movie as MovieSchema
from movie_library.utils.movie import create_movie, delete_movie, get_movie, update_movie


class TestMovieDB:
    @staticmethod
    def get_movie_sample() -> dict:
        return MovieSchema.parse_obj({"title": "Title!", "description": "good movie"})

    @staticmethod
    def process_movies_sample(movie) -> dict:
        return MovieSchema(title=movie.title, description=movie.description)

    async def test_get_movie_success(self, migrated_postgres, session, movies_sample):
        movie = await get_movie(session, movies_sample[0].id)

        assert movie.title == movies_sample[0].title
        assert movie.description == movies_sample[0].description

    async def test_get_movie_no_movie(self, migrated_postgres, session):
        movie = await get_movie(session, uuid4())
        assert movie is None

    async def test_create_movie_success(self, migrated_postgres, session):
        movie = self.get_movie_sample()
        result = await create_movie(session, movie)

        assert movie.title == result.title
        assert movie.description == result.description

    async def test_create_movie_exists(self, migrated_postgres, session, movies_sample):
        result = await create_movie(session, self.process_movies_sample(movies_sample[0]))
        assert result is None

    async def test_delete_movie(self, migrated_postgres, session, movies_sample):
        result = await delete_movie(session, movies_sample[0].id)
        assert result == 1

    async def test_delete_movie_no_movie(self, migrated_postgres, session):
        result = await delete_movie(session, str(uuid4()))
        assert result == 0

    @pytest.mark.parametrize("field", ["title", "description"])
    async def test_update_movie(self, migrated_postgres, session, movies_sample, field):
        modified_movie = MovieSchema(title=movies_sample[0].title, description=movies_sample[0].description)
        setattr(modified_movie, field, "new_" + getattr(movies_sample[0], field))

        is_updated, _ = await update_movie(session, movies_sample[0].id, modified_movie)
        assert is_updated

    async def test_update_movie_no_movie(self, migrated_postgres, session):
        modified_movie = MovieSchema(title="title", description="description")

        is_updated, message = await update_movie(session, uuid4(), modified_movie)
        assert is_updated is None
        assert message == "Movie does not exist!"

    async def test_update_movie_title_taken(self, migrated_postgres, session, movies_sample):
        modified_movie = MovieSchema(title=movies_sample[0].title, description=movies_sample[0].description)
        modified_movie.title = movies_sample[1].title

        is_updated, message = await update_movie(session, movies_sample[0].id, modified_movie)
        assert not is_updated
        assert message == "Title already exists."
