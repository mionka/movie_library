from fastapi import FastAPI
from fastapi_pagination import add_pagination
from uvicorn import run

from movie_library.config import DefaultSettings, get_settings
from movie_library.endpoints import list_of_routes
from movie_library.utils.common import get_hostname


def bind_routes(application: FastAPI, setting: DefaultSettings) -> None:
    """
    Bind all routes to application.
    """
    for route in list_of_routes:
        application.include_router(route, prefix=setting.PATH_PREFIX)


def get_app() -> FastAPI:
    """
    Creates application and all dependable objects.
    """
    description = "Сервис, реализующий фильмотеку."

    tags_metadata = [
        {
            "name": "Application Health",
            "description": "API health check.",
        },
    ]

    application = FastAPI(
        title="Movie Library",
        description=description,
        docs_url="/swagger",
        openapi_url="/openapi",
        version="0.1.0",
        openapi_tags=tags_metadata,
    )
    settings = get_settings()
    bind_routes(application, settings)
    add_pagination(application)
    application.state.settings = settings
    return application


app = get_app()

if __name__ == "__main__":
    settings_for_application = get_settings()
    run(
        "movie_library.__main__:app",
        host=get_hostname(settings_for_application.APP_HOST),
        port=settings_for_application.APP_PORT,
        reload=True,
        reload_dirs=["movie_library", "tests"],
        log_level="debug",
    )
