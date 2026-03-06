"""FastAPI application entry point"""

from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from app.core.config import get_settings
from app.core.database import init_db, close_db
from app.api.v1.router import api_router
from app.core.exceptions import SuperstarException
import os
from scripts.init_data import init_db_data

settings = get_settings()

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await init_db()
    # Initialize sample data
    init_db_data()
    yield
    # Shutdown
    await close_db()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
    # 启用 docs 和 redoc，但浏览器需要能访问外部 CDN
    # 如果无法访问外网，可以使用 /openapi.json 查看 API 定义
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Attach rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
from app.middleware.error_handler import (
    http_exception_handler,
    validation_exception_handler,
    superstar_exception_handler,
    general_exception_handler
)
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

app.add_exception_handler(SuperstarException, superstar_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Middleware
from app.middleware.logging import LoggingMiddleware
app.add_middleware(LoggingMiddleware)


# Include API routes
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Mount static files for uploaded images
app.mount("/static", StaticFiles(directory="static"), name="static")

# Static files (if static_dist exists)
static_dist_path = Path(__file__).parent.parent / "static_dist"
if static_dist_path.exists() and (static_dist_path / "index.html").exists():
    # Mount static files directory at root to serve assets correctly
    # This allows /assets/... paths in HTML to work
    app.mount("/assets", StaticFiles(directory=str(static_dist_path / "assets")), name="assets")
    
    # Serve index.html for root path
    @app.get("/")
    async def read_root():
        """Serve frontend index.html"""
        index_path = static_dist_path / "index.html"
        return FileResponse(str(index_path))
    
    # SPA fallback: serve index.html for all non-API routes
    # Note: FastAPI automatically handles /docs, /redoc, /openapi.json
    # This route should only catch frontend routes, not API or docs routes
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """SPA fallback: serve index.html for all non-API routes"""
        # Don't serve index.html for API routes, static files, or assets
        # FastAPI's /docs, /redoc, /openapi.json are handled automatically
        if full_path.startswith("api/") or full_path.startswith("assets/"):
            return JSONResponse({"detail": "Not Found"}, status_code=404)
        
        # Serve index.html for frontend routes
        index_path = static_dist_path / "index.html"
        return FileResponse(str(index_path))
else:
    # Frontend not built yet - show helpful message
    @app.get("/")
    async def read_root():
        """Frontend not available"""
        return {
            "message": "Superstar V15.1 API",
            "version": settings.APP_VERSION,
            "status": "Backend is running",
            "frontend": "Frontend not built. Please build frontend first.",
            "endpoints": {
                "health": "/health",
                "api_docs": "/docs",
                "api": "/api/v1"
            }
        }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": settings.APP_VERSION}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)