from datetime import datetime, timezone
from fastapi import APIRouter
from app.schemas.common import HealthResponse, ServiceStatusSchema
from app.core.config import settings
from app.db.session import check_database_health

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def get_health():
    """
    Service health check endpoint.
    Per architectural requirement: Health must never require a configured production database to run.
    """
    db_status = await check_database_health()
    overall_status = "ok" if db_status in ("ok", "unconfigured") else "degraded"

    return HealthResponse(
        status=overall_status,
        version=settings.app_version,
        environment=settings.roamly_env,
        timestamp=datetime.now(timezone.utc),
        services=ServiceStatusSchema(
            api="ok",
            database=db_status,
        ),
    )
