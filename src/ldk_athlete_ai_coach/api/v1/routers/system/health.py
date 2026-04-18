"""Health-check endpoints for API v1."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Return health status for service monitoring.

    Returns:
        dict[str, str]: Health status payload.

    """
    return {"status": "ok"}
