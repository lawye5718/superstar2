"""Error handlers for FastAPI"""

import logging
import traceback
import uuid

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.core.exceptions import SuperstarException


async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation exceptions"""
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": exc.errors()
        }
    )


async def superstar_exception_handler(request: Request, exc: SuperstarException):
    """Handle custom Superstar exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message}
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions — logs full stack trace for diagnosis"""
    request_id = str(uuid.uuid4())
    logging.error(
        f"[{request_id}] Unhandled exception: {exc}\n"
        f"Request: {request.method} {request.url}\n"
        f"Traceback:\n{traceback.format_exc()}"
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "request_id": request_id,
        }
    )