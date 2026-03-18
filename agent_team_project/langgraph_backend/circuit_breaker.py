"""
熔断器 (P3-B4)：CLOSED / OPEN / HALF_OPEN 状态机。
与 design.md 第 11 章一致。
"""
from __future__ import annotations

import threading
import time
from enum import Enum
from typing import Dict


class CircuitBreaker:
    """熔断器：连续失败达阈值打开，超时后半开试探，成功达阈值关闭。"""

    class State(Enum):
        CLOSED = "closed"
        OPEN = "open"
        HALF_OPEN = "half_open"

    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        success_threshold: int = 3,
        timeout: float = 60.0,
        half_open_max_calls: int = 3,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.success_threshold = success_threshold
        self.timeout = timeout
        self.half_open_max_calls = half_open_max_calls
        self._state = self.State.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time = 0.0
        self._half_open_calls = 0
        self._lock = threading.Lock()

    def can_execute(self) -> bool:
        with self._lock:
            if self._state == self.State.CLOSED:
                return True
            if self._state == self.State.OPEN:
                if time.time() - self._last_failure_time >= self.timeout:
                    self._state = self.State.HALF_OPEN
                    self._half_open_calls = 0
                    self._success_count = 0
                    return True
                return False
            if self._state == self.State.HALF_OPEN:
                if self._half_open_calls < self.half_open_max_calls:
                    self._half_open_calls += 1
                    return True
                return False
            return True

    def record_success(self) -> None:
        with self._lock:
            if self._state == self.State.HALF_OPEN:
                self._success_count += 1
                self._half_open_calls -= 1
                if self._success_count >= self.success_threshold:
                    self._state = self.State.CLOSED
                    self._failure_count = 0
            else:
                self._failure_count = 0

    def record_failure(self) -> None:
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.time()
            if self._state == self.State.HALF_OPEN:
                self._half_open_calls -= 1
                self._state = self.State.OPEN
            elif self._state == self.State.CLOSED and self._failure_count >= self.failure_threshold:
                self._state = self.State.OPEN

    def get_state(self) -> dict:
        with self._lock:
            return {
                "name": self.name,
                "state": self._state.value,
                "failure_count": self._failure_count,
                "success_count": self._success_count,
                "last_failure_time": self._last_failure_time,
                "half_open_calls": self._half_open_calls,
            }


class CircuitBreakerRegistry:
    def __init__(self):
        self._breakers: Dict[str, CircuitBreaker] = {}
        self._lock = threading.Lock()

    def get_or_create(
        self,
        name: str,
        failure_threshold: int = 5,
        success_threshold: int = 3,
        timeout: float = 60.0,
    ) -> CircuitBreaker:
        with self._lock:
            if name not in self._breakers:
                self._breakers[name] = CircuitBreaker(
                    name=name,
                    failure_threshold=failure_threshold,
                    success_threshold=success_threshold,
                    timeout=timeout,
                )
            return self._breakers[name]

    def get_all_status(self) -> dict:
        return {n: b.get_state() for n, b in self._breakers.items()}
