import pytest
from starlette import status


class TestUserHandler:
    @staticmethod
    def get_url(current_endpoint: str) -> str:
        return "/api/v1/user/" + current_endpoint

    @staticmethod
    def get_user_sample() -> dict:
        return {"username": "example-user", "password": "example123", "email": "user@example.com"}

    @staticmethod
    def get_auth_data(user: dict) -> dict:
        return {"username": user["username"], "password": user["password"]}

    @staticmethod
    def get_auth_header(token_info: dict) -> dict:
        token_type = token_info["token_type"].capitalize()
        token = token_info["access_token"]
        return {"Authorization": " ".join([token_type, token])}

    async def test_registration_success(self, client):
        endpoint_path = "registration"

        response = await client.post(url=self.get_url(endpoint_path), json=self.get_user_sample())
        assert response.status_code == status.HTTP_201_CREATED

    async def test_registration_user_exists(self, client):
        endpoint_path = "registration"

        response = await client.post(url=self.get_url(endpoint_path), json=self.get_user_sample())
        assert response.status_code == status.HTTP_201_CREATED

        response = await client.post(url=self.get_url(endpoint_path), json=self.get_user_sample())
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    async def test_authentification_success(self, client, users_sample):
        endpoint_path = "authentication"
        data = self.get_auth_data(users_sample[0])

        response = await client.post(url=self.get_url(endpoint_path), data=data)
        assert response.status_code == status.HTTP_200_OK

    async def test_authentification_wrong_password(self, client, users_sample):
        endpoint_path = "authentication"

        data = self.get_auth_data(users_sample[0])
        data["password"] += "_wrong"

        response = await client.post(url=self.get_url(endpoint_path), data=data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_authentification_user_not_found(self, client):
        endpoint_path = "authentication"

        data = self.get_auth_data(self.get_user_sample())

        response = await client.post(url=self.get_url(endpoint_path), data=data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_current_user_success(self, client, users_sample):
        endpoint_path = "authentication"
        data = self.get_auth_data(users_sample[0])

        response = await client.post(url=self.get_url(endpoint_path), data=data)
        assert response.status_code == status.HTTP_200_OK

        endpoint_path = "me"
        headers = self.get_auth_header(response.json())

        response = await client.get(url=self.get_url(endpoint_path), headers=headers)
        assert response.status_code == status.HTTP_200_OK

    async def test_get_current_user_no_user(self, client):
        endpoint_path = "me"
        response = await client.get(url=self.get_url(endpoint_path))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_takeout_user_success(self, client, users_sample):
        endpoint_path = "authentication"
        data = self.get_auth_data(users_sample[0])

        response = await client.post(url=self.get_url(endpoint_path), data=data)
        assert response.status_code == status.HTTP_200_OK

        endpoint_path = "takeout"
        headers = self.get_auth_header(response.json())

        response = await client.delete(url=self.get_url(endpoint_path), headers=headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    async def test_takeout_user_no_user(self, client):
        endpoint_path = "takeout"

        response = await client.delete(url=self.get_url(endpoint_path))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.parametrize("field", ["username", "password", "email"])
    async def test_update_user(self, client, users_sample, field):
        endpoint_path = "authentication"
        data = self.get_auth_data(users_sample[0])

        response = await client.post(url=self.get_url(endpoint_path), data=data)
        assert response.status_code == status.HTTP_200_OK

        endpoint_path = "edit"
        headers = self.get_auth_header(response.json())
        modified_user = {
            "username": users_sample[0]["username"],
            "email": users_sample[0]["email"],
        }
        modified_user[field] = "new_" + users_sample[0][field]

        response = await client.put(url=self.get_url(endpoint_path), headers=headers, json=modified_user)
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize("field", ["username", "email"])
    async def test_update_user_is_taken(self, client, users_sample, field):
        endpoint_path = "authentication"
        data = self.get_auth_data(users_sample[0])

        response = await client.post(url=self.get_url(endpoint_path), data=data)
        assert response.status_code == status.HTTP_200_OK

        endpoint_path = "edit"
        headers = self.get_auth_header(response.json())
        modified_user = {
            "username": users_sample[0]["username"],
            "email": users_sample[0]["email"],
        }
        modified_user[field] = users_sample[1][field]

        response = await client.put(url=self.get_url(endpoint_path), headers=headers, json=modified_user)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
