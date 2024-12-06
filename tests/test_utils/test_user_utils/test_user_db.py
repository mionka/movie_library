# pylint: disable=unused-argument

import pytest

from movie_library.db.models import User
from movie_library.schemas import RegistrationForm, UserEdit
from movie_library.utils.user import delete_user, get_user, register_user, update_user


class TestUserDB:
    @staticmethod
    def get_user_sample() -> dict:
        return RegistrationForm.parse_obj(
            {"username": "example_user", "password": "12341234", "email": "user@example.com"}
        )

    async def test_get_user_success(self, migrated_postgres, session, users_sample):
        user = await get_user(session, username=users_sample[0]["username"])
        assert user.username == users_sample[0]["username"]

    async def test_get_user_no_user(self, migrated_postgres, session, users_sample):
        user = await get_user(session, username="not_" + users_sample[0]["username"])
        assert user is None

    async def test_register_user_success(self, migrated_postgres, session):
        is_registered, message = await register_user(session, self.get_user_sample())

        assert is_registered
        assert message == "Successful registration!"

    async def test_register_user_exists(self, migrated_postgres, session):
        await register_user(session, self.get_user_sample())
        is_registered, message = await register_user(session, self.get_user_sample())

        assert not is_registered
        assert message == "Username or email already exists."

    async def test_delete_user(self, migrated_postgres, session, users_sample):
        user_to_delete = User(username=users_sample[0]["username"])

        res = await delete_user(session, user_to_delete)
        assert res == 1

    async def test_delete_user_no_user(self, migrated_postgres, session):
        user_to_delete = User(username=self.get_user_sample().username)

        res = await delete_user(session, user_to_delete)
        assert res == 0

    @pytest.mark.parametrize("field", ["username", "password", "email"])
    async def test_update_user(self, migrated_postgres, session, users_sample, field):
        user_to_update = User(**users_sample[0])
        modified_user = users_sample[0]
        modified_user[field] = "new_" + modified_user[field]
        is_updated, _ = await update_user(session, user_to_update, UserEdit(**modified_user))
        assert is_updated

    async def test_update_user_no_user(self, migrated_postgres, session):
        user_to_update = User(username="random_name")
        modified_user = {"username": "username", "email": "email@example.com"}
        is_updated, _ = await update_user(session, user_to_update, UserEdit(**modified_user))
        assert is_updated

    @pytest.mark.parametrize(
        "field, expected_message", [("username", "Username already exists."), ("email", "Email is taken.")]
    )
    async def test_update_user_is_taken(
        self,
        migrated_postgres,
        session,
        users_sample,
        field,
        expected_message,
    ):
        user_to_update = User(**users_sample[0])
        modified_user = users_sample[0]
        modified_user[field] = users_sample[1][field]
        is_updated, message = await update_user(session, user_to_update, UserEdit(**modified_user))
        assert not is_updated
        assert message == expected_message
