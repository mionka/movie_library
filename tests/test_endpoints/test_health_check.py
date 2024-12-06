import pytest
from starlette import status


class TestHealthCheckHandler:
    @staticmethod
    def get_url(current_endpoint: str) -> str:
        return "/api/v1/health_check/" + current_endpoint

    @pytest.mark.parametrize("endpoint_path", ["ping_application", "ping_database"])
    async def test_check_health(self, client, endpoint_path):
        response = await client.get(url=self.get_url(endpoint_path))
        assert response.status_code == status.HTTP_200_OK
