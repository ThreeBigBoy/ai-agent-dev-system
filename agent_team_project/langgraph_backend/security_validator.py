"""
安全验证器 (P3-A1)：输入校验、XSS/SQLi 防护。
与 design.md 第 11 章一致。
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, List


class SecurityValidator:
    """输入验证与安全防护：长度、XSS、SQL 注入、危险模式。"""

    DEFAULT_CONFIG = {
        "max_input_length": 10 * 1024 * 1024,  # 10MB 单字段
        "max_file_size_mb": 50,
        "allowed_html_tags": [],
        "forbidden_patterns": [
            r"<script[^>]*>.*?</script>",
            r"DROP\s+TABLE",
            r"DELETE\s+FROM",
            r"rm\s+-rf\s+/",
            r"__import__\s*\(",
            r"eval\s*\(",
            r"exec\s*\(",
        ],
    }

    def __init__(self, config: Dict[str, Any] | None = None):
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}
        self._forbidden = [
            re.compile(p, re.IGNORECASE | re.DOTALL)
            for p in self.config["forbidden_patterns"]
        ]

    def validate_input(
        self,
        user_input: Any,
        context: str = "general",
    ) -> Dict[str, Any]:
        """
        Returns:
            {"valid": bool, "sanitized": str|None, "errors": list, "warnings": list}
        """
        errors: List[str] = []
        warnings: List[str] = []
        if not isinstance(user_input, (str, int, float, bool, list, dict)):
            return {
                "valid": False,
                "sanitized": None,
                "errors": [f"不支持的输入类型: {type(user_input).__name__}"],
                "warnings": [],
            }
        if not isinstance(user_input, str):
            return {"valid": True, "sanitized": str(user_input), "errors": [], "warnings": []}
        sanitized = user_input
        max_len = self.config["max_input_length"]
        if len(user_input) > max_len:
            errors.append(f"输入长度 {len(user_input)} 超过最大值 {max_len}")
            sanitized = user_input[:max_len]
        for pattern in self._forbidden:
            m = pattern.search(sanitized)
            if m:
                errors.append(f"检测到危险内容: {m.group(0)[:50]}...")
                sanitized = pattern.sub("[REMOVED]", sanitized)
        if "<" in sanitized or ">" in sanitized:
            if not self.config["allowed_html_tags"]:
                warnings.append("包含 HTML 标签，已转义")
                sanitized = sanitized.replace("<", "&lt;").replace(">", "&gt;")
        return {
            "valid": len(errors) == 0,
            "sanitized": sanitized,
            "errors": errors,
            "warnings": warnings,
        }

    def validate_file_size(self, file_path: Path) -> Dict[str, Any]:
        max_bytes = self.config["max_file_size_mb"] * 1024 * 1024
        if not file_path.exists():
            return {"valid": False, "error": "文件不存在"}
        size = file_path.stat().st_size
        if size > max_bytes:
            return {
                "valid": False,
                "error": f"文件大小 {size/1024/1024:.1f}MB 超过限制 {self.config['max_file_size_mb']}MB",
            }
        return {"valid": True, "size": size}
