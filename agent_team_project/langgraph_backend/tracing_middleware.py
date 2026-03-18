"""
全链路追踪中间件 (P3-C2)：为 FastAPI 注入 TraceContext，记录请求耗时。
与 design.md 第 11 章一致。
"""
from __future__ import annotations

import time
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from .trace_context import TraceContext

# 请求作用域 key
TRACE_CONTEXT_KEY = "trace_context"


class TracingMiddleware(BaseHTTPMiddleware):
    """从 Header 读取或生成 request_id，写入 Request.state，并在响应头回传。"""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = request.headers.get("x-request-id") or None
        trace = TraceContext(request_id=request_id)
        trace.add_tag("path", request.url.path)
        trace.add_tag("method", request.method)
        request.state.trace_context = trace  # type: ignore
        start = time.time()
        response = await call_next(request)
        trace.record_span("http_request", start, time.time(), status="ok")
        response.headers["x-request-id"] = trace.request_id
        response.headers["x-span-id"] = trace.span_id
        return response
