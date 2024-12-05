from movie_library.endpoints.favorite import api_router as fav_router
from movie_library.endpoints.health_check import api_router as health_router
from movie_library.endpoints.movie import api_router as movie_router
from movie_library.endpoints.user import api_router as user_router


list_of_routes = [
    health_router,
    user_router,
    movie_router,
    fav_router,
]


__all__ = [
    "list_of_routes",
]
