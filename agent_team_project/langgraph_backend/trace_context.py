"""
全链路追踪上下文 (P3-C1)：RequestID / SpanID / 性能计时。
与 design.md 第 11 章一致。
"""
from __future__ import annotations

import time
import uuid
from typing import Any, Dict, List, Optional


class TraceContext:
    """请求 ID、Span、标签、耗时。"""

    def __init__(
        self,
        request_id: Optional[str] = None,
        parent_span_id: Optional[str] = None,
    ):
        self.request_id = request_id or str(uuid.uuid4()).replace("-", "")[:16]
        self.span_id = str(uuid.uuid4()).replace("-", "")[:8]
        self.parent_span_id = parent_span_id
        self.start_time = time.time()
        self.spans: List[dict] = []
        self.tags: Dict[str, Any] = {}

    def child_span(self, operation: str) -> "TraceContext":
        child = TraceContext(request_id=self.request_id, parent_span_id=self.span_id)
        child.tags["operation"] = operation
        child.tags["parent_operation"] = self.tags.get("operation", "root")
        return child

    def record_span(
        self,
        operation: str,
        start_time: float,
        end_time: float,
        status: str = "ok",
        error: Optional[str] = None,
    ) -> dict:
        span = {
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "operation": operation,
            "start_time": start_time,
            "end_time": end_time,
            "duration_ms": (end_time - start_time) * 1000,
            "status": status,
            "error": error,
            "tags": self.tags.copy(),
        }
        self.spans.append(span)
        return span

    def add_tag(self, key: str, value: Any) -> None:
        self.tags[key] = value

    def get_elapsed_ms(self) -> float:
        return (time.time() - self.start_time) * 1000

    def to_dict(self) -> dict:
        return {
            "request_id": self.request_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "elapsed_ms": self.get_elapsed_ms(),
            "span_count": len(self.spans),
            "tags": self.tags,
            "spans": self.spans,
        }
