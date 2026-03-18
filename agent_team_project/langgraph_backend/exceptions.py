"""
应用层异常 (P3-B2)
与 design.md 第 11 章一致，携带 ErrorCode，供全局异常处理与 API 响应使用。
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from .error_codes import ErrorCode


class AppException(Exception):
    """
    应用层异常基类
    所有业务/安全/系统异常应使用此类，便于统一 HTTP 状态与响应体。
    """

    def __init__(
        self,
        error_code: ErrorCode,
        detail: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ):
        self.error_code = error_code
        self.detail = detail or error_code.message
        self.extra = extra or {}
        super().__init__(self.detail)

    def to_response(self) -> dict:
        """转为 HTTP 响应体（与 ErrorCode.to_dict 一致）"""
        return self.error_code.to_dict(detail=self.detail, extra=self.extra or None)
