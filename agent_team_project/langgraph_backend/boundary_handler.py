"""
边界条件处理器 (P3-D1~D4)：文件大小、磁盘、Python 版本、内存。
与 design.md 第 11 章一致。
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List


class BoundaryConditionHandler:
    """超大文件、磁盘、版本、内存检查。"""

    def __init__(self, workspace_root: Path):
        self.workspace_root = Path(workspace_root)

    def check_all_boundaries(self, change_id: str = "") -> dict:
        checks = []
        blocking: List[str] = []
        checks.append(self._check_disk_space())
        if not checks[-1]["passed"]:
            blocking.append(checks[-1]["message"])
        checks.append(self._check_python_version())
        if not checks[-1]["passed"]:
            blocking.append(checks[-1]["message"])
        checks.append(self._check_memory())
        if not checks[-1]["passed"]:
            blocking.append(checks[-1]["message"])
        return {
            "passed": len(blocking) == 0,
            "checks": checks,
            "blocking_issues": blocking,
        }

    def _check_disk_space(self, min_free_gb: float = 1.0) -> dict:
        try:
            import shutil
            usage = shutil.disk_usage(self.workspace_root)
            free_gb = usage.free / (1024**3)
            passed = free_gb >= min_free_gb
            return {
                "name": "disk_space",
                "passed": passed,
                "message": f"磁盘可用 {free_gb:.2f} GB" if passed else f"磁盘空间不足: {free_gb:.2f} GB < {min_free_gb} GB",
                "free_gb": free_gb,
                "severity": "critical" if not passed else "info",
            }
        except Exception as e:
            return {"name": "disk_space", "passed": False, "message": str(e), "severity": "critical"}

    def _check_python_version(self, min_version: tuple = (3, 9)) -> dict:
        cur = sys.version_info[:2]
        passed = cur >= min_version
        return {
            "name": "python_version",
            "passed": passed,
            "message": f"Python {cur}" if passed else f"Python {cur} < {min_version} (需要 >= 3.9)",
            "current": list(cur),
            "required": list(min_version),
            "severity": "critical" if not passed else "info",
        }

    def _check_memory(self, min_available_mb: float = 500) -> dict:
        try:
            import psutil
            mem = psutil.virtual_memory()
            avail_mb = mem.available / (1024 * 1024)
            passed = avail_mb >= min_available_mb
            return {
                "name": "memory",
                "passed": passed,
                "message": f"可用内存 {avail_mb:.0f} MB" if passed else f"可用内存不足: {avail_mb:.0f} MB < {min_available_mb} MB",
                "available_mb": round(avail_mb, 2),
                "severity": "critical" if not passed else "info",
            }
        except ImportError:
            return {"name": "memory", "passed": True, "message": "未安装 psutil，跳过", "severity": "info"}
        except Exception as e:
            return {"name": "memory", "passed": False, "message": str(e), "severity": "critical"}

    def check_file_size(self, file_path: Path, max_mb: float = 100) -> dict:
        """单文件大小边界（P3-D1）。"""
        if not file_path.exists():
            return {"passed": False, "message": "文件不存在"}
        size_mb = file_path.stat().st_size / (1024 * 1024)
        passed = size_mb <= max_mb
        return {
            "passed": passed,
            "size_mb": round(size_mb, 2),
            "max_mb": max_mb,
            "message": f"文件 {size_mb:.1f} MB" if passed else f"文件超过 {max_mb} MB 限制",
        }
