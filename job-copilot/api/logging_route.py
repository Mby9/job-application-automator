import time
from typing import Callable
from fastapi import Request, Response
from fastapi.routing import APIRoute
from core.logger_config import get_logger

logger = get_logger("http_logger")

class LoggingRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            body = await request.body()
            body_str = body.decode('utf-8')[:1000] if body else ""
            if request.url.path != "/api/health":
                logger.info(f"REQ {request.method} {request.url.path} | {body_str}")
                
            start = time.perf_counter()
            response: Response = await original_route_handler(request)
            elapsed_ms = (time.perf_counter() - start) * 1000

            resp_body = getattr(response, "body", b"")
            resp_str = resp_body.decode('utf-8')[:1000] if resp_body else "<Streaming>"
            
            if request.url.path != "/api/health":
                logger.info(f"RES {request.url.path} -> {response.status_code} ({elapsed_ms:.1f}ms) | {resp_str}")
                
            return response

        return custom_route_handler
