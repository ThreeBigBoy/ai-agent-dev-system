"""
统一错误码体系 (P3-B1)
与 design.md 第 11 章一致，供 AppException 与 HTTP 异常处理使用。
"""
from __future__ import annotations

import time
from enum import Enum
from typing import Any, Dict, Optional


class ErrorCode(Enum):
    """
    统一错误码体系
    格式: XXX_YYYYY — XXX: 类别 (SYS/BIZ/EXT/SEC)，YYYYY: 编号
    """

    # 系统错误 (SYS)
    SYS_INTERNAL_ERROR = ("SYS_00001", "系统内部错误", 500)
    SYS_SERVICE_UNAVAILABLE = ("SYS_00002", "服务暂时不可用", 503)
    SYS_TIMEOUT = ("SYS_00003", "操作超时", 504)
    SYS_RESOURCE_EXHAUSTED = ("SYS_00004", "系统资源耗尽", 503)
    SYS_CONFIGURATION_ERROR = ("SYS_00005", "配置错误", 500)

    # 业务错误 (BIZ)
    BIZ_INVALID_PARAMETER = ("BIZ_00001", "参数校验失败", 400)
    BIZ_RESOURCE_NOT_FOUND = ("BIZ_00002", "资源不存在", 404)
    BIZ_STATE_INVALID = ("BIZ_00003", "状态不合法", 409)
    BIZ_VERSION_CONFLICT = ("BIZ_00004", "版本冲突", 409)
    BIZ_DUPLICATE_REQUEST = ("BIZ_00005", "重复请求", 429)

    # 外部服务错误 (EXT)
    EXT_MCP_UNAVAILABLE = ("EXT_00001", "MCP服务不可用", 503)
    EXT_AGENT_INVOCATION_FAILED = ("EXT_00002", "Agent调用失败", 502)
    EXT_BACKEND_TIMEOUT = ("EXT_00003", "后端服务超时", 504)
    EXT_NETWORK_ERROR = ("EXT_00004", "网络错误", 502)

    # 安全错误 (SEC)
    SEC_UNAUTHORIZED = ("SEC_00001", "未授权访问", 401)
    SEC_FORBIDDEN = ("SEC_00002", "权限不足", 403)
    SEC_INPUT_VALIDATION_FAILED = ("SEC_00003", "输入验证失败", 400)
    SEC_RATE_LIMIT_EXCEEDED = ("SEC_00004", "请求频率超限", 429)
    SEC_SUSPICIOUS_ACTIVITY = ("SEC_00005", "检测到可疑活动", 403)

    def __init__(self, code: str, message: str, http_status: int):
        self.code = code
        self.message = message
        self.http_status = http_status

    def to_dict(
        self,
        detail: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> dict:
        """转为标准错误响应体"""
        result = {
            "error_code": self.code,
            "error_message": self.message,
            "http_status": self.http_status,
            "timestamp": time.time(),
        }
        if detail:
            result["detail"] = detail
        if extra:
            result["extra"] = extra
        return result
