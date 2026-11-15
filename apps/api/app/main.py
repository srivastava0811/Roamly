from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.logging import logger, setup_logging
from app.core.exceptions import RoamlyException
from app.db.base import Base
from app.db.session import engine
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.router import api_v1_router
# Import all models so Base metadata has them registered
import app.models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging(settings.roamly_env)
    logger.info(f"Starting {settings.app_name} v{settings.app_version} in [{settings.roamly_env}] mode")
    
    # In local development with SQLite, create tables if they do not exist
    if "sqlite" in settings.database_url:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Initialized local SQLite database schema")

    yield

    logger.info(f"Shutting down {settings.app_name}")
    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend API for Roamly AI Travel Operating System",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS configuration with explicit allowed origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.api_cors_origins if isinstance(settings.api_cors_origins, list) else [settings.api_cors_origins],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


@app.exception_handler(RoamlyException)
async def roamly_exception_handler(request: Request, exc: RoamlyException):
    headers = {}
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        headers["WWW-Authenticate"] = "Bearer"

    return JSONResponse(
        status_code=exc.status_code,
        headers=headers,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception on {request.method} {request.url}: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected server error occurred.",
            }
        },
    )


# Root health router (accessible at /health)
app.include_router(health_router)

# Versioned API routes
app.include_router(api_v1_router)
