import os
from pathlib import Path
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import settings
from backend.app.core.exceptions import (
    DartaChalanException,
    DocumentNotFoundError,
    PermissionDeniedError,
    InvalidBSDateError,
    StorageError,
    OCRProcessingError,
    SequenceGenerationError,
)
from backend.app.api.routes import api_router
from backend.app.db.base import Base, engine
import backend.app.db  # Ensure all models are imported

from contextlib import asynccontextmanager
from backend.app.services.smtp_scanner import smtp_scanner_service
from backend.app.core.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure DB tables exist
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        logger.warning(f"Notice: Initial table check skipped or running in test environment: {e}")

    # Startup: Start Inbound SMTP Scanner Daemon if enabled
    if settings.SMTP_SCANNER_ENABLED:
        try:
            await smtp_scanner_service.start()
        except Exception as e:
            logger.error(f"Could not initialize SMTP Scanner on startup: {e}")
    yield
    # Shutdown: Stop Inbound SMTP Scanner
    if smtp_scanner_service.is_running:
        try:
            await smtp_scanner_service.stop()
        except Exception as e:
            logger.error(f"Error terminating SMTP Scanner on shutdown: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Enterprise-grade Darta (Incoming) and Chalan (Outgoing) Digitization API for Nepal Telecom Corporation",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Configuration
origins = settings.CORS_ORIGINS if settings.CORS_ORIGINS else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Exception Handlers
@app.exception_handler(DartaChalanException)
async def custom_exception_handler(request: Request, exc: DartaChalanException):
    status_code = status.HTTP_400_BAD_REQUEST
    if isinstance(exc, DocumentNotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, PermissionDeniedError):
        status_code = status.HTTP_403_FORBIDDEN
    elif isinstance(exc, (InvalidBSDateError, StorageError, OCRProcessingError, SequenceGenerationError)):
        status_code = status.HTTP_400_BAD_REQUEST
    
    return JSONResponse(
        status_code=status_code,
        content={"detail": exc.message}
    )

# Include API Router
app.include_router(api_router, prefix="/api/v1")
# Also mount under /api for backwards compatibility / frontend convenience
app.include_router(api_router, prefix="/api")

@app.get("/health", tags=["System"])
@app.get("/api/v1/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "system": settings.PROJECT_NAME,
        "version": settings.VERSION
    }

# Mount Frontend Static SPA if dist directory is available
BASE_DIR = Path(__file__).resolve().parent.parent.parent
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"

if FRONTEND_DIST.exists():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa_frontend(request: Request, full_path: str):
        # Exclude API endpoints, Swagger, and OpenAPI docs from SPA catch-all
        if (
            full_path.startswith("api/")
            or full_path.startswith("docs")
            or full_path.startswith("redoc")
            or full_path.startswith("openapi.json")
            or full_path == "health"
        ):
            return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": "Not Found"})

        # Check if direct static file exists in dist (e.g. favicon, vite.svg)
        potential_file = FRONTEND_DIST / full_path
        if full_path and potential_file.is_file():
            return FileResponse(str(potential_file))

        # Fallback to index.html for React Router SPA routes
        index_file = FRONTEND_DIST / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": "Frontend index.html not found. Please run 'npm run build' inside frontend/"}
        )

