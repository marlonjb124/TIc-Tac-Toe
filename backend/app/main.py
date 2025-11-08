"""
Main FastAPI application entry point.
Implements clean architecture and dependency injection patterns.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events for the application.
    """
    # Startup
    print(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Debug mode: {settings.DEBUG}")

    # Initialize database connection pool (to be implemented)
    # await database.connect()

    yield

    # Shutdown
    print("Shutting down application")
    # Close database connections
    # await database.disconnect()


def create_application() -> FastAPI:
    """
    Application factory pattern.
    Creates and configures the FastAPI application instance.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url=f"{settings.API_V1_PREFIX}/docs",
        redoc_url=f"{settings.API_V1_PREFIX}/redoc",
        lifespan=lifespan,
        debug=settings.DEBUG,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers (to be added in future commits)
    # app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return app


# Create application instance
app = create_application()


@app.get("/health", tags=["Health"])
async def health_check() -> JSONResponse:
    """
    Health check endpoint.
    """
    return JSONResponse(
        content={
            "status": "healthy",
            "version": settings.VERSION,
            "environment": settings.ENVIRONMENT,
        }
    )


@app.get("/", tags=["Root"])
async def root() -> dict:
    """
    Root endpoint.
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs",
    }
