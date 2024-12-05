# pylint: disable=unused-argument

from movie_library.config.utils import get_settings
from movie_library.utils.user import authenticate_user, create_access_token, get_current_user, verify_password


class TestUserLogic:
    @staticmethod
    def get_user_sample() -> dict:
        return {"username": "example_user", "password": "12341234", "email": "user@example.com"}

    @staticmethod
    def hash_password(password: str) -> str:
        settings = get_settings()
        hashed_password = settings.PWD_CONTEXT.hash(password)

        return hashed_password

    async def test_authenticate_user_success(self, migrated_postgres, session, users_sample):
        user = users_sample[0]
        result = await authenticate_user(session, user["username"], user["password"])
        assert result.username == users_sample[0]["username"]

    async def test_authenticate_user_no_user(self, migrated_postgres, session):
        user = self.get_user_sample()
        result = await authenticate_user(session, user["username"], user["password"])
        assert not result

    async def test_authenticate_user_wrong_password(self, migrated_postgres, session, users_sample):
        user = users_sample[0]
        result = await authenticate_user(session, user["username"], user["password"] + "_wrong")
        assert not result

    async def test_get_current_user_success(self, migrated_postgres, session, users_sample):
        user = users_sample[0]
        token = create_access_token(data={"sub": user["username"]})

        current_user = await get_current_user(session, token)
        assert current_user.username == user["username"]

    def test_create_access_token_success(self):
        token = create_access_token(data={"sub": "example-user"})
        assert token is not None

    def test_verify_password_right(self):
        user = self.get_user_sample()
        hashed_password = self.hash_password(user["password"])

        result = verify_password(user["password"], hashed_password)
        assert result

    def test_verify_password_wrong(self):
        user = self.get_user_sample()
        hashed_password = self.hash_password(user["password"])

        result = verify_password("not_" + user["password"], hashed_password)
        assert not result
