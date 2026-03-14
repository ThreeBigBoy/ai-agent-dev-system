#!/usr/bin/env python3
"""MCP server for LangGraph backend: tools to call /run, /status, /health (HTTP)."""

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

# 调用 /run、/resume 时的 HTTP 超时（秒），可通过环境变量 LANGGRAPH_HTTP_TIMEOUT 覆盖（默认 300）
_DEFAULT_HTTP_TIMEOUT = 300


def _get_http_timeout() -> int:
    try:
        return int(os.environ.get("LANGGRAPH_HTTP_TIMEOUT", _DEFAULT_HTTP_TIMEOUT))
    except ValueError:
        return _DEFAULT_HTTP_TIMEOUT

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Please install mcp: pip install mcp", file=sys.stderr)
    sys.exit(1)

# 默认后端地址（与 langgraph_backend/server.py 一致）
DEFAULT_BASE = "http://127.0.0.1:8000"


def _http_post(url: str, data: dict) -> dict:
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=_get_http_timeout()) as r:
        return json.loads(r.read().decode("utf-8"))


def _http_get(url: str) -> dict:
    req = urllib.request.Request(url, method="GET")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def _format_run_response(res: dict) -> str:
    """将 /run 响应格式化为可读字符串，便于注入 Cursor Chat。"""
    status = res.get("status", "unknown")
    change_id = res.get("change_id", "")
    thread_id = res.get("thread_id")
    checkpoint_id = res.get("checkpoint_id")
    feedback = res.get("feedback", "")
    results = res.get("results", [])
    latency = res.get("latency_seconds", 0)
    lines = [
        f"**LangGraph 后端执行结果**",
        f"- change_id: {change_id}",
        f"- status: {status}",
        f"- latency_seconds: {latency}",
        f"- 任务数: {len(results)}",
    ]
    if thread_id or checkpoint_id:
        lines.append(f"- thread_id: {thread_id or '—'}（断点续跑用）")
        lines.append(f"- checkpoint_id: {checkpoint_id or '—'}（断点续跑用）")
    lines.extend(["", "**反馈摘要**", feedback or "（无）"])
    if results:
        lines.append("")
        lines.append("**各任务结果**")
        for r in results[:20]:
            tid = r.get("task_id", "")
            ex = r.get("executor", "")
            st = r.get("status", "")
            fb = (r.get("feedback") or r.get("output") or "")[:100]
            lines.append(f"- 任务 {tid}（{ex}）: {st} — {fb}")
        if len(results) > 20:
            lines.append(f"- ... 共 {len(results)} 条")
    return "\n".join(lines)


mcp = FastMCP(
    "langgraph-backend",
    description="调用 LangGraph 独立后端执行变更任务（/run、/status、/health）",
)


# 业务项目配置：支持两种形式
# 1) JSON 数组字符串：[{"LANGGRAPH_PROJECT_KEY":"k","LANGGRAPH_WORKSPACE_ROOT":"/path"},...]，配合 LANGGRAPH_CURRENT_PROJECT_KEY 表示当前项目
# 2) 扁平字符串：key1|path1:key2|path2（兼容），未设 current 时由后端按 change_id 自动解析
_ENV_WORKSPACE_PROJECTS = "LANGGRAPH_WORKSPACE_PROJECTS"
_ENV_CURRENT_PROJECT_KEY = "LANGGRAPH_CURRENT_PROJECT_KEY"
_LEGACY_ENV_WORKSPACE_ROOT = "LANGGRAPH_WORKSPACE_ROOT"


def _parse_projects_from_env() -> tuple[list[tuple[str, str]], str | None]:
    """
    从环境解析业务项目列表与当前项目 key。
    返回 ([(project_key, root), ...], current_project_key_or_none)。
    """
    current = (os.environ.get(_ENV_CURRENT_PROJECT_KEY) or "").strip() or None
    raw = (os.environ.get(_ENV_WORKSPACE_PROJECTS) or "").strip()
    if not raw:
        return ([], current)
    # JSON 数组格式：[{"LANGGRAPH_PROJECT_KEY":"k","LANGGRAPH_WORKSPACE_ROOT":"/path"},...]
    if raw.startswith("["):
        try:
            arr = json.loads(raw)
            if not isinstance(arr, list):
                return ([], current)
            pairs: list[tuple[str, str]] = []
            for item in arr:
                if isinstance(item, dict):
                    k = (item.get("LANGGRAPH_PROJECT_KEY") or item.get("project_key") or "").strip()
                    r = (item.get("LANGGRAPH_WORKSPACE_ROOT") or item.get("workspace_root") or "").strip()
                    if k and r:
                        pairs.append((k, r))
            return (pairs, current)
        except (json.JSONDecodeError, TypeError):
            pass
    # 扁平格式：key1|path1:key2|path2
    for sep in (":", ";"):
        if sep in raw:
            parts = [p.strip() for p in raw.split(sep) if p.strip()]
            break
    else:
        parts = [raw]
    pairs = []
    for p in parts:
        if "|" in p:
            key, _, path = p.partition("|")
            key, path = key.strip(), path.strip()
            if key and path:
                pairs.append((key, path))
    return (pairs, current)


def _resolve_workspace_projects_or_root(workspace_root: str | None) -> tuple[str | None, str | None]:
    """
    解析 MCP 配置为请求体字段。始终优先本仓（由后端保证）。
    - 若设置了 LANGGRAPH_CURRENT_PROJECT_KEY：只传该当前项目对应的 workspace_root（单路径）。
    - 若未设 current：传 workspace_projects 整串，由后端按 change_id 自动解析。
    兼容：显式传参 workspace_root、或仅 LANGGRAPH_WORKSPACE_ROOT 单路径。
    返回 (workspace_projects_raw, workspace_root_legacy)。
    """
    explicit_root = (workspace_root or "").strip()
    if explicit_root:
        return (None, explicit_root)
    pairs, current_key = _parse_projects_from_env()
    if not pairs:
        legacy = (os.environ.get(_LEGACY_ENV_WORKSPACE_ROOT) or "").strip()
        return (None, legacy if legacy else None)
    if current_key:
        for k, root in pairs:
            if k == current_key:
                return (None, root)
        return (None, None)
    flat = ":".join(f"{k}|{r}" for k, r in pairs)
    return (flat, None)


@mcp.tool()
def run_langgraph(
    change_id: str,
    task_range: str | None = None,
    workspace_root: str | None = None,
    base_url: str = DEFAULT_BASE,
) -> str:
    """
    调用 LangGraph 后端执行指定 change_id 的任务。

    - change_id: 变更 ID（如 migrate-langgraph-backend 或业务项目的 update-theme-v1.0.2-mvp-health-compliance）
    - task_range: 可选，如 "2.1-2.4" 或 "2.1" 只执行该范围
    - workspace_root: 可选；未传时从 MCP 配置解析。传参时直接作为项目根路径（兼容单项目）。
    - base_url: 后端地址，默认 http://127.0.0.1:8000

    配置范式（~/.cursor/mcp.json 的 langgraph-backend.env）：
    - 优先本仓：后端始终先读本仓 openspec/changes，再试业务项目。
    - 多业务项目：仅配置 **LANGGRAPH_WORKSPACE_PROJECTS** 即可（JSON 数组串或扁平 key|path 串），后端按 change_id 自动解析；可选 LANGGRAPH_CURRENT_PROJECT_KEY 固定当前项目时只传该 root。
    - 仅在本仓迭代时不设或留空。兼容：可仍用 LANGGRAPH_WORKSPACE_ROOT 单路径。
    留痕写入 runtime-logs/langgraph-runs/，含 resolved project_key。
    """
    url = f"{base_url.rstrip('/')}/run"
    try:
        workspace_projects_raw, workspace_root_legacy = _resolve_workspace_projects_or_root(workspace_root)
        body = {"change_id": change_id}
        if task_range:
            body["task_range"] = task_range
        if workspace_projects_raw:
            body["workspace_projects"] = workspace_projects_raw
        elif workspace_root_legacy:
            body["workspace_root"] = workspace_root_legacy
        res = _http_post(url, body)
        return _format_run_response(res)
    except urllib.error.HTTPError as e:
        err_body = ""
        try:
            err_body = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        out = f"**调用失败**：HTTP {e.code}\n{err_body or str(e)}"
        if e.code == 400 and "tasks.md" in (err_body or ""):
            out += "\n\n**提示**：若该 change-id 属于**业务项目**，请在 **~/.cursor/mcp.json** 的 **langgraph-backend.env** 中配置 **LANGGRAPH_WORKSPACE_PROJECTS**（格式：\"project_key|项目根路径:key2|路径2\"），后端会按 change_id 自动从列表中解析出对应项目，无需单独设置当前项目。"
        return out
    except urllib.error.URLError as e:
        return f"**调用失败**：无法连接后端 {url}\n请确认已启动：`cd agent_team_project && source .venv/bin/activate && uvicorn langgraph_backend.server:app --port 8000`\n错误: {e}"
    except Exception as e:
        return f"**调用失败**：{type(e).__name__}: {e}"


@mcp.tool()
def resume_langgraph(change_id: str, thread_id: str, checkpoint_id: str, base_url: str = DEFAULT_BASE) -> str:
    """
    从检查点恢复执行（断点续跑）。需使用上次 /run 返回的 thread_id 与 checkpoint_id。

    - change_id: 变更 ID
    - thread_id: 线程 ID（run_langgraph 返回的 thread_id）
    - checkpoint_id: 检查点 ID（run_langgraph 返回的 checkpoint_id）
    - base_url: 后端地址，默认 http://127.0.0.1:8000
    """
    url = f"{base_url.rstrip('/')}/resume"
    try:
        res = _http_post(url, {"change_id": change_id, "thread_id": thread_id, "checkpoint_id": checkpoint_id})
        return _format_run_response(res)
    except urllib.error.URLError as e:
        return f"**调用失败**：无法连接后端 {url}\n错误: {e}"
    except Exception as e:
        return f"**调用失败**：{type(e).__name__}: {e}"


@mcp.tool()
def get_langgraph_status(change_id: str, base_url: str = DEFAULT_BASE) -> str:
    """
    查询 LangGraph 后端某 change_id 的执行状态。

    - change_id: 变更 ID
    - base_url: 后端地址，默认 http://127.0.0.1:8000
    """
    url = f"{base_url.rstrip('/')}/status/{change_id}"
    try:
        res = _http_get(url)
        return json.dumps(res, ensure_ascii=False, indent=2)
    except urllib.error.URLError as e:
        return f"无法连接后端: {e}"
    except Exception as e:
        return f"{type(e).__name__}: {e}"


@mcp.tool()
def langgraph_health(base_url: str = DEFAULT_BASE) -> str:
    """
    探测 LangGraph 后端健康状态。

    - base_url: 后端地址，默认 http://127.0.0.1:8000
    """
    url = f"{base_url.rstrip('/')}/health"
    try:
        res = _http_get(url)
        return json.dumps(res, ensure_ascii=False, indent=2)
    except urllib.error.URLError as e:
        return f"后端未就绪: {e}"
    except Exception as e:
        return f"{type(e).__name__}: {e}"


if __name__ == "__main__":
    mcp.run(transport="stdio")
