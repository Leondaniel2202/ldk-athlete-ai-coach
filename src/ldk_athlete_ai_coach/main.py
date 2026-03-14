from fastapi import FastAPI

from ldk_athlete_ai_coach.api.router import api_router


def create_application() -> FastAPI:
    app = FastAPI(title="ldk-athlete-ai-coach")
    app.include_router(api_router, prefix="/api")

    @app.get("/", tags=["root"])
    async def read_root() -> dict[str, str]:
        return {"message": "ldk-athlete-ai-coach backend"}

    return app


app = create_application()
