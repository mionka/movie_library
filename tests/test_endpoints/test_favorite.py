from uuid import uuid4

from starlette import status

from movie_library.utils.user import create_access_token


class TestFavoriteHandler:
    @staticmethod
    def get_url(current_endpoint: str = "") -> str:
        return "/api/v1/favorite/" + current_endpoint

    @staticmethod
    def get_auth_data(user: dict) -> dict:
        return {"username": user["username"], "password": user["password"]}

    @staticmethod
    def get_auth_header(token_info: dict) -> dict:
        token_type = token_info["token_type"].capitalize()
        token = token_info["access_token"]
        return {"Authorization": " ".join([token_type, token])}

    @staticmethod
    def get_token_data(username) -> dict:
        return {"sub": username}

    @staticmethod
    def get_favorites_settings(page: int = 1, size: int = 50) -> str:
        return f"page={page}&size={size}"

    async def test_add_favorite_success(self, client, users_sample, movies_sample):
        access_token = create_access_token(data=self.get_token_data(users_sample[0]["username"]))
        headers = self.get_auth_header({"token_type": "bearer", "access_token": access_token})

        response = await client.post(url=self.get_url(str(movies_sample[0].id)), headers=headers)
        assert response.status_code == status.HTTP_201_CREATED

    async def test_add_favorite_twice(self, client, users_sample, movies_sample):
        access_token = create_access_token(data=self.get_token_data(users_sample[0]["username"]))
        headers = self.get_auth_header({"token_type": "bearer", "access_token": access_token})

        response = await client.post(url=self.get_url(str(movies_sample[0].id)), headers=headers)
        assert response.status_code == status.HTTP_201_CREATED

        response = await client.post(url=self.get_url(str(movies_sample[0].id)), headers=headers)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_add_favorite_no_movie(self, client, users_sample):
        access_token = create_access_token(data=self.get_token_data(users_sample[0]["username"]))
        headers = self.get_auth_header({"token_type": "bearer", "access_token": access_token})

        response = await client.post(url=self.get_url(str(uuid4())), headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_delete_favorite_success(self, client, favorites_sample):
        favorites, user = favorites_sample
        access_token = create_access_token(data=self.get_token_data(user["username"]))
        headers = self.get_auth_header({"token_type": "bearer", "access_token": access_token})

        response = await client.delete(url=self.get_url(str(favorites[0].movie_id)), headers=headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_delete_favorite_no_movie(self, client, users_sample):
        access_token = create_access_token(data=self.get_token_data(users_sample[0]["username"]))
        headers = self.get_auth_header({"token_type": "bearer", "access_token": access_token})

        response = await client.delete(url=self.get_url(str(uuid4())), headers=headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_get_favorites_one_page(self, client, favorites_sample):
        favorites, user = favorites_sample
        request_settings = self.get_favorites_settings()

        access_token = create_access_token(data=self.get_token_data(user["username"]))
        headers = self.get_auth_header({"token_type": "bearer", "access_token": access_token})
        response = await client.get(url=f"{self.get_url()}?{request_settings}", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["pages"] == 1
        assert len(response.json()["items"]) == len(favorites)

    async def test_get_favorites_several_pages(self, client, favorites_sample):
        favorites, user = favorites_sample
        request_settings = self.get_favorites_settings(size=1)

        access_token = create_access_token(data=self.get_token_data(user["username"]))
        headers = self.get_auth_header({"token_type": "bearer", "access_token": access_token})
        response = await client.get(url=f"{self.get_url()}?{request_settings}", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["pages"] == len(favorites)
        assert len(response.json()["items"]) == 1

    async def test_get_favorites_empty(self, client, users_sample):
        request_settings = self.get_favorites_settings()

        access_token = create_access_token(data=self.get_token_data(users_sample[0]["username"]))
        headers = self.get_auth_header({"token_type": "bearer", "access_token": access_token})
        response = await client.get(url=f"{self.get_url()}?{request_settings}", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        print("lelele", response.json())
        assert response.json()["pages"] == 0
        assert len(response.json()["items"]) == 0
