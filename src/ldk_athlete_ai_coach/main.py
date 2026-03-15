"""Application entrypoint for the FastAPI backend."""

from fastapi import FastAPI

from ldk_athlete_ai_coach.api.router import api_router
from ldk_athlete_ai_coach.core.config import get_settings
from ldk_athlete_ai_coach.core.logging import configure_logging


def create_application() -> FastAPI:
    """Create and configure the FastAPI application instance.

    Returns:
        FastAPI: Configured application object.
    """
    settings = get_settings()
    configure_logging(debug=settings.debug)

    app = FastAPI(
        debug=settings.debug,
        title=settings.app_name,
    )
    app.include_router(api_router, prefix="/api")

    @app.get("/", tags=["root"])
    async def read_root() -> dict[str, str]:
        """Return a simple service status message.

        Returns:
            dict[str, str]: Root endpoint payload.
        """
        return {"message": f"{settings.app_name} backend"}

    return app


app = create_application()
