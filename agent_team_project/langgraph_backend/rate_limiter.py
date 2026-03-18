"""
限流器 (P3-B3)：令牌桶，全局/变更/用户级。
与 design.md 第 11 章一致。
"""
from __future__ import annotations

import threading
import time
from typing import Dict, Any

from .error_codes import ErrorCode


class RateLimiter:
    """多级限流：global / change / user，令牌桶。"""

    def __init__(self):
        self.global_config = {"rate": 100, "burst": 200, "enabled": True}
        self.change_config = {"rate": 20, "burst": 50, "enabled": True}
        self.user_config = {"rate": 10, "burst": 30, "enabled": True}
        self._buckets: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def _key(self, level: str, identifier: str) -> str:
        return f"{level}:{identifier}"

    def _check_and_consume(self, level: str, identifier: str, config: dict) -> bool:
        if not config.get("enabled", True):
            return True
        now = time.time()
        rate = config["rate"]
        burst = config["burst"]
        key = self._key(level, identifier)
        with self._lock:
            if key not in self._buckets:
                self._buckets[key] = {"tokens": float(burst), "last_update": now}
            b = self._buckets[key]
            elapsed = now - b["last_update"]
            b["tokens"] = min(b["tokens"] + elapsed * rate, burst)
            b["last_update"] = now
            if b["tokens"] >= 1:
                b["tokens"] -= 1
                return True
            return False

    def check_rate_limit(
        self,
        change_id: str | None = None,
        user_id: str | None = None,
    ) -> dict:
        limits = []
        if not self._check_and_consume("global", "all", self.global_config):
            limits.append({"level": "global", "allowed": False})
            return {
                "allowed": False,
                "reason": "系统全局流量超限",
                "limits": limits,
                "error_code": ErrorCode.SEC_RATE_LIMIT_EXCEEDED.code,
            }
        limits.append({"level": "global", "allowed": True})
        if change_id and not self._check_and_consume("change", change_id, self.change_config):
            limits.append({"level": "change", "allowed": False})
            return {
                "allowed": False,
                "reason": f"变更 {change_id} 请求频率超限",
                "limits": limits,
                "error_code": ErrorCode.SEC_RATE_LIMIT_EXCEEDED.code,
            }
        if change_id:
            limits.append({"level": "change", "allowed": True, "change_id": change_id})
        if user_id and not self._check_and_consume("user", user_id, self.user_config):
            limits.append({"level": "user", "allowed": False})
            return {
                "allowed": False,
                "reason": f"用户 {user_id} 请求频率超限",
                "limits": limits,
                "error_code": ErrorCode.SEC_RATE_LIMIT_EXCEEDED.code,
            }
        if user_id:
            limits.append({"level": "user", "allowed": True, "user_id": user_id})
        return {"allowed": True, "reason": "通过所有限流检查", "limits": limits}
