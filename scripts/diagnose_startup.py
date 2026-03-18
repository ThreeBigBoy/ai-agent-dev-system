#!/usr/bin/env python3
"""
启动问题自动诊断脚本 (V2.11.1)
对应 tasks.md P2-B：6 项诊断，输出 JSON/Table。
错误码见 design.md 第 9 章。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# 错误码（与 design 一致）
ERR_DISK_SPACE = "DIAG_001"
ERR_PYTHON_VERSION = "DIAG_002"
ERR_MEMORY = "DIAG_003"
ERR_NETWORK = "DIAG_004"
ERR_CONFIG = "DIAG_005"
ERR_PORT = "DIAG_006"


def check_disk_space(workspace_root: Path, min_free_gb: float = 1.0) -> dict:
    """P2-B1: 磁盘空间诊断。低于 min_free_gb 告警。"""
    try:
        import shutil
        usage = shutil.disk_usage(workspace_root)
        free_gb = usage.free / (1024**3)
        ok = free_gb >= min_free_gb
        return {
            "id": "disk-space",
            "ok": ok,
            "code": None if ok else ERR_DISK_SPACE,
            "message": f"磁盘可用 {free_gb:.2f} GB" if ok else f"磁盘空间不足: {free_gb:.2f} GB 可用 (建议 ≥{min_free_gb} GB)",
            "fix": None if ok else "清理磁盘或扩展存储",
        }
    except Exception as e:
        return {
            "id": "disk-space",
            "ok": False,
            "code": ERR_DISK_SPACE,
            "message": str(e),
            "fix": "检查路径权限与磁盘",
        }


def check_python_version(min_version: tuple = (3, 9)) -> dict:
    """P2-B2: Python 版本诊断。低于 3.9 不通过。"""
    cur = sys.version_info[:2]
    ok = cur >= min_version
    return {
        "id": "python-version",
        "ok": ok,
        "code": None if ok else ERR_PYTHON_VERSION,
        "message": f"Python {sys.version.split()[0]}" if ok else f"Python 版本过低: {cur} (需要 >= {min_version})",
        "fix": None if ok else "升级 Python 到 3.9 或更高",
    }


def check_memory_available(min_available_gb: float = 1.0) -> dict:
    """P2-B3: 可用内存诊断。"""
    try:
        import psutil
        mem = psutil.virtual_memory()
        available_gb = mem.available / (1024**3)
        ok = available_gb >= min_available_gb
        return {
            "id": "memory-available",
            "ok": ok,
            "code": None if ok else ERR_MEMORY,
            "message": f"可用内存 {available_gb:.2f} GB" if ok else f"可用内存不足: {available_gb:.2f} GB (建议 ≥{min_available_gb} GB)",
            "fix": None if ok else "关闭其他应用释放内存",
        }
    except ImportError:
        return {
            "id": "memory-available",
            "ok": True,
            "code": None,
            "message": "未安装 psutil，跳过内存检查",
            "fix": None,
        }
    except Exception as e:
        return {
            "id": "memory-available",
            "ok": False,
            "code": ERR_MEMORY,
            "message": str(e),
            "fix": "检查系统内存",
        }


def check_network_connectivity(timeout: float = 5.0) -> dict:
    """P2-B4: 网络连通性诊断（示例：对后端 health 的连通性）。"""
    try:
        import urllib.request
        urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=timeout)
        return {
            "id": "network-connectivity",
            "ok": True,
            "code": None,
            "message": "后端 8000 健康检查可达",
            "fix": None,
        }
    except Exception as e:
        return {
            "id": "network-connectivity",
            "ok": False,
            "code": ERR_NETWORK,
            "message": f"后端不可达或超时: {e!s}",
            "fix": "确认 LangGraph 后端已启动: uvicorn langgraph_backend.server:app --port 8000",
        }


def check_config_validation(workspace_root: Path) -> dict:
    """P2-B5: 配置校验（AGENT_TEAM_PROJECT_ROOT / openspec 等）。"""
    import os
    root_env = os.environ.get("AGENT_TEAM_PROJECT_ROOT", "").strip()
    if root_env and Path(root_env).is_dir():
        has_openspec = (Path(root_env) / "openspec" / "changes").is_dir()
        ok = has_openspec
        return {
            "id": "config-validation",
            "ok": ok,
            "code": None if ok else ERR_CONFIG,
            "message": f"AGENT_TEAM_PROJECT_ROOT 已设置且 openspec/changes 存在" if ok else "AGENT_TEAM_PROJECT_ROOT 下未找到 openspec/changes",
            "fix": None if ok else "设置 AGENT_TEAM_PROJECT_ROOT 为仓库根（含 openspec/changes）",
        }
    candidate = workspace_root
    if (candidate / "openspec" / "changes").is_dir():
        return {
            "id": "config-validation",
            "ok": True,
            "code": None,
            "message": f"使用工作区根 {candidate}，openspec/changes 存在",
            "fix": None,
        }
    return {
        "id": "config-validation",
        "ok": False,
        "code": ERR_CONFIG,
        "message": "AGENT_TEAM_PROJECT_ROOT 未设置且当前路径下无 openspec/changes",
        "fix": "export AGENT_TEAM_PROJECT_ROOT=/path/to/ai-agent-dev-system",
    }


def check_port_availability(ports: list[int] = (8000, 8001)) -> dict:
    """P2-B6: 端口可用性诊断。"""
    import socket
    busy = []
    for port in ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                busy.append(port)
    ok = len(busy) == 0
    return {
        "id": "port-availability",
        "ok": ok,
        "code": None if ok else ERR_PORT,
        "message": f"端口 {ports} 可用" if ok else f"端口 {busy} 已被占用",
        "fix": None if ok else f"释放端口: lsof -ti:{busy[0]} | xargs kill -9",
    }


def run_all_checks(workspace_root: Path | None = None) -> dict:
    """执行全部 6 项诊断，返回统一结构。"""
    root = workspace_root or Path.cwd()
    results = [
        check_disk_space(root),
        check_python_version(),
        check_memory_available(),
        check_network_connectivity(),
        check_config_validation(root),
        check_port_availability(),
    ]
    healthy = all(r["ok"] for r in results)
    return {
        "healthy": healthy,
        "checks": results,
        "summary": {
            "total": len(results),
            "passed": sum(1 for r in results if r["ok"]),
            "failed": sum(1 for r in results if not r["ok"]),
        },
    }


def format_table(data: dict) -> str:
    """P2-B8: 表格形式输出。"""
    lines = [
        "【启动诊断结果】",
        "",
        "| 检查项 | 状态 | 说明 |",
        "|--------|------|------|",
    ]
    for c in data["checks"]:
        status = "✅" if c["ok"] else "❌"
        msg = (c["message"] or "")[:60]
        lines.append(f"| {c['id']} | {status} | {msg} |")
    lines.append("")
    lines.append(f"通过: {data['summary']['passed']}/{data['summary']['total']}，健康: {'是' if data['healthy'] else '否'}")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="启动问题自动诊断 (V2.11.1)")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    parser.add_argument("--workspace", type=Path, default=None, help="工作区根目录，默认 cwd")
    args = parser.parse_args()
    root = args.workspace or Path.cwd()
    data = run_all_checks(root)
    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(format_table(data))
    sys.exit(0 if data["healthy"] else 1)


if __name__ == "__main__":
    main()
