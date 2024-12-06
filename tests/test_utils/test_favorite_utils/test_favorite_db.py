# pylint: disable=unused-argument

from uuid import uuid4

from movie_library.db.models import User
from movie_library.utils.favorite import add_favorite, delete_favorite, get_favorites_query


class TestFavoriteDB:
    @staticmethod
    def convert_user(user: dict) -> User:
        return User(**user)

    async def test_add_favorite_success(self, migrated_postgres, session, users_sample, movies_sample):
        result = await add_favorite(session, self.convert_user(users_sample[0]), movies_sample[0].id)
        assert result

    async def test_add_favorite_twice(self, migrated_postgres, session, users_sample, movies_sample):
        result = await add_favorite(session, self.convert_user(users_sample[0]), movies_sample[0].id)
        assert result
        result = await add_favorite(session, self.convert_user(users_sample[0]), movies_sample[0].id)
        assert not result

    async def test_add_favorite_no_movie(self, migrated_postgres, session, users_sample):
        result = await add_favorite(session, self.convert_user(users_sample[0]), uuid4())
        assert result is None

    async def test_delete_favorite_success(self, migrated_postgres, session, favorites_sample):
        favorites, user = favorites_sample
        result = await delete_favorite(session, self.convert_user(user), favorites[0].movie_id)
        assert result == 1

    async def test_delete_favorite_no_movie(self, migrated_postgres, session, users_sample):
        result = await delete_favorite(session, self.convert_user(users_sample[0]), uuid4())
        assert result == 0

    async def test_get_favorites_query_success(self, migrated_postgres, session, users_sample):
        result = await get_favorites_query(session, self.convert_user(users_sample[0]))
        assert result.whereclause.right.value == users_sample[0]["id"]
