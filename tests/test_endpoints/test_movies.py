# pylint: disable=duplicate-code
from uuid import uuid4

import pytest
from starlette import status

from movie_library.utils.user import create_access_token


class TestMovieHandler:
    @staticmethod
    def get_url(current_endpoint: str = "") -> str:
        return "/api/v1/movie/" + current_endpoint

    @staticmethod
    def get_movie_sample() -> dict:
        return {"title": "Title!", "description": "good movie"}

    @staticmethod
    def process_movies_sample(movie) -> dict:
        return {"title": movie.title, "description": movie.description}

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

    async def test_get_movie_success(self, client, users_sample, movies_sample):
        access_token = create_access_token(data=self.get_token_data(users_sample[0]["username"]))
        headers = self.get_auth_header({"token_type": "bearer", "access_token": access_token})

        response = await client.get(url=self.get_url(movies_sample[0].id), headers=headers)
        assert response.status_code == status.HTTP_200_OK

    async def test_get_movie_no_movie(self, client, users_sample):
        access_token = create_access_token(data=self.get_token_data(users_sample[0]["username"]))
        headers = self.get_auth_header({"token_type": "bearer", "access_token": access_token})

        response = await client.get(url=self.get_url(str(uuid4())), headers=headers)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_create_movie_success(self, client, users_sample):
        access_token = create_access_token(data=self.get_token_data(users_sample[0]["username"]))
        headers = self.get_auth_header({"token_type": "bearer", "access_token": access_token})

        expected_movie = self.get_movie_sample()
        response = await client.post(url=self.get_url(), headers=headers, json=expected_movie)
        response_data = response.json()
        assert response.status_code == status.HTTP_201_CREATED
        assert response_data["title"] == expected_movie["title"]
        assert response_data["description"] == expected_movie["description"]

    async def test_create_movie_exists(self, client, users_sample, movies_sample):
        access_token = create_access_token(data=self.get_token_data(users_sample[0]["username"]))
        headers = self.get_auth_header({"token_type": "bearer", "access_token": access_token})

        response = await client.post(
            url=self.get_url(), headers=headers, json=self.process_movies_sample(movies_sample[0])
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_delete_movie(self, client, users_sample, movies_sample):
        access_token = create_access_token(data=self.get_token_data(users_sample[0]["username"]))
        headers = self.get_auth_header({"token_type": "bearer", "access_token": access_token})

        response = await client.delete(url=self.get_url(movies_sample[0].id), headers=headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_delete_movie_no_movie(self, client, users_sample):
        access_token = create_access_token(data=self.get_token_data(users_sample[0]["username"]))
        headers = self.get_auth_header({"token_type": "bearer", "access_token": access_token})

        response = await client.delete(url=self.get_url(str(uuid4())), headers=headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_get_movies_one_page(self, client, users_sample, movies_sample):
        request_settings = self.get_favorites_settings()

        access_token = create_access_token(data=self.get_token_data(users_sample[0]["username"]))
        headers = self.get_auth_header({"token_type": "bearer", "access_token": access_token})
        response = await client.get(url=f"{self.get_url()}?{request_settings}", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["pages"] == 1
        assert len(response.json()["items"]) == len(movies_sample)

    async def test_get_movies_several_pages(self, client, users_sample, movies_sample):
        request_settings = self.get_favorites_settings(size=1)

        access_token = create_access_token(data=self.get_token_data(users_sample[0]["username"]))
        headers = self.get_auth_header({"token_type": "bearer", "access_token": access_token})
        response = await client.get(url=f"{self.get_url()}?{request_settings}", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["pages"] == len(movies_sample)
        assert len(response.json()["items"]) == 1

    async def test_get_movies_empty(self, client, users_sample):
        request_settings = self.get_favorites_settings()

        access_token = create_access_token(data=self.get_token_data(users_sample[0]["username"]))
        headers = self.get_auth_header({"token_type": "bearer", "access_token": access_token})
        response = await client.get(url=f"{self.get_url()}?{request_settings}", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["pages"] == 0
        assert len(response.json()["items"]) == 0

    @pytest.mark.parametrize("field", ["title", "description"])
    async def test_update_movie(self, client, users_sample, movies_sample, field):
        access_token = create_access_token(data=self.get_token_data(users_sample[0]["username"]))
        headers = self.get_auth_header({"token_type": "bearer", "access_token": access_token})

        modified_movie = {
            "title": movies_sample[0].title,
            "description": movies_sample[0].description,
        }
        modified_movie[field] = "new_" + modified_movie[field]

        response = await client.put(
            url=self.get_url(f"edit/{movies_sample[0].id}"), headers=headers, json=modified_movie
        )

        assert response.status_code == status.HTTP_200_OK

    async def test_update_movie_no_movie(self, client, users_sample, movies_sample):
        access_token = create_access_token(data=self.get_token_data(users_sample[0]["username"]))
        headers = self.get_auth_header({"token_type": "bearer", "access_token": access_token})

        modified_movie = {
            "title": movies_sample[0].title,
            "description": movies_sample[0].description,
        }
        response = await client.put(url=self.get_url(f"edit/{str(uuid4())}"), headers=headers, json=modified_movie)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    async def test_update_title_taken(self, client, users_sample, movies_sample):
        access_token = create_access_token(data=self.get_token_data(users_sample[0]["username"]))
        headers = self.get_auth_header({"token_type": "bearer", "access_token": access_token})

        modified_movie = {
            "title": movies_sample[0].title,
            "description": movies_sample[0].description,
        }
        modified_movie["title"] = movies_sample[1].title

        response = await client.put(
            url=self.get_url(f"edit/{movies_sample[0].id}"), headers=headers, json=modified_movie
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
