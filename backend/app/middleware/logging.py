"""Logging middleware"""

import time
import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()
        
        # Log the incoming request
        logging.info(f"Request: {request.method} {request.url}")
        
        response = None
        try:
            response = await call_next(request)
            
            # Calculate process time
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log the response
            logging.info(f"Response: {response.status_code} - Process time: {process_time:.4f}s")
            
            return response
        except Exception as e:
            # Calculate process time even on error
            process_time = time.time() - start_time
            
            # Log any exceptions
            logging.error(f"Request failed: {request.method} {request.url} - {str(e)}")
            logging.error(f"Process time before error: {process_time:.4f}s")
            raise