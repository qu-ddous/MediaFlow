"""Structured request logging middleware."""

from __future__ import annotations

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("mediaflow.access")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Logs incoming HTTP requests with latency, status code, and IP."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time = time.time()
        client_ip = request.client.host if request.client else "unknown"
        method = request.method
        path = request.url.path

        try:
            response = await call_next(request)
            duration_ms = round((time.time() - start_time) * 1000, 2)
            logger.info(
                "%s %s %d - %s ms (IP: %s)",
                method,
                path,
                response.status_code,
                duration_ms,
                client_ip,
            )
            return response
        except Exception as exc:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            logger.error(
                "%s %s 500 - %s ms (IP: %s) Error: %s",
                method,
                path,
                duration_ms,
                client_ip,
                exc,
            )
            raise exc
