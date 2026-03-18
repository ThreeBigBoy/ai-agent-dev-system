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
    from mcp.types import CallToolResult, TextContent
except ImportError:
    print("Please install mcp: pip install mcp", file=sys.stderr)
    sys.exit(1)


def _tool_result(text: str, is_error: bool = False) -> CallToolResult:
    """返回 MCP 协议规定的 CallToolResult，避免 Cursor 解析 CallToolRequest 时得到 undefined。"""
    return CallToolResult(
        content=[TextContent(type="text", text=text)],
        isError=is_error,
    )

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


def _append_hints_if_error(text: str) -> str:
    """
    检测响应文本中的特定错误模式，追加标准提示。
    保持「显式脚本、显式 SOP」原则：只追加提示文案，不自动执行副作用操作。
    """
    import re
    # 检测依赖缺失错误（langchain-openai / langchain_openai）
    dep_patterns = [
        r"未安装\s*langchain[\-_]openai",
        r"langchain[\-_]openai",
        r"ImportError.*langchain",
        r"ModuleNotFoundError.*langchain",
    ]
    has_dep_error = any(re.search(p, text, re.IGNORECASE) for p in dep_patterns)

    # 检测路径/配置错误（AGENT_TEAM_PROJECT_ROOT / openspec/changes）
    path_patterns = [
        r"未找到\s*openspec/changes",
        r"AGENT_TEAM_PROJECT_ROOT",
        r"未设置\s*AGENT_TEAM",
        r"找不到.*openspec",
    ]
    has_path_error = any(re.search(p, text, re.IGNORECASE) for p in path_patterns)

    hints = []
    if has_dep_error:
        hints.append(
            "\n\n**【环境修复提示】** 检测到后端缺少必要依赖（如 langchain-openai）。"
            "请在 agent_team_project 目录下执行 `bash setup-langgraph-env.sh` 安装依赖，"
            "再用 `./start-langgraph-backend.sh` 重启后端。"
        )
    if has_path_error:
        hints.append(
            "\n\n**【配置修复提示】** 检测到后端无法找到项目路径或 AGENT_TEAM_PROJECT_ROOT 未正确设置。"
            "请检查：1) AGENT_TEAM_PROJECT_ROOT 环境变量是否指向 ai-agent-dev-system 仓库根；"
            "2) 或检查 ~/.cursor/mcp.json 中的 LANGGRAPH_WORKSPACE_PROJECTS 配置是否正确。"
        )

    if hints:
        return text + "".join(hints)
    return text


# FastMCP 仅传 name（部分 mcp 版本不支持 description 参数）
mcp = FastMCP("langgraph-backend")


@mcp.resource("langgraph-backend://info")
def _resource_backend_info() -> str:
    """MCP 资源：返回后端说明，用于满足 ListResourcesRequest 协议，避免 Cursor 报错。"""
    return json.dumps({
        "server": "langgraph-backend",
        "description": "LangGraph workflow backend MCP: run_langgraph, resume_langgraph, health, human_confirm_*",
    }, ensure_ascii=False, indent=2)


@mcp.prompt()
def _prompt_backend_info() -> str:
    """MCP 提示：返回后端说明，用于满足 ListPromptsRequest 协议，避免 Cursor 报 undefined。"""
    return "LangGraph 后端 MCP 可用工具：run_langgraph、resume_langgraph、health、human_confirm_poll、human_confirm_submit。"


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
) -> CallToolResult:
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
        formatted = _format_run_response(res)
        return _tool_result(_append_hints_if_error(formatted))
    except urllib.error.HTTPError as e:
        err_body = ""
        try:
            err_body = e.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        out = f"**调用失败**：HTTP {e.code}\n{err_body or str(e)}"
        if e.code == 400 and "tasks.md" in (err_body or ""):
            out += "\n\n**提示**：若该 change-id 属于**业务项目**，请在 **~/.cursor/mcp.json** 的 **langgraph-backend.env** 中配置 **LANGGRAPH_WORKSPACE_PROJECTS**（格式：\"project_key|项目根路径:key2|路径2\"），后端会按 change_id 自动从列表中解析出对应项目，无需单独设置当前项目。"
        return _tool_result(out, is_error=True)
    except urllib.error.URLError as e:
        return _tool_result(f"**调用失败**：无法连接后端 {url}\n请确认已启动：`cd agent_team_project && source .venv/bin/activate && uvicorn langgraph_backend.server:app --port 8000`\n错误: {e}", is_error=True)
    except Exception as e:
        return _tool_result(f"**调用失败**：{type(e).__name__}: {e}", is_error=True)


@mcp.tool()
def resume_langgraph(change_id: str, thread_id: str, checkpoint_id: str, base_url: str = DEFAULT_BASE) -> CallToolResult:
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
        formatted = _format_run_response(res)
        return _tool_result(_append_hints_if_error(formatted))
    except urllib.error.URLError as e:
        return _tool_result(f"**调用失败**：无法连接后端 {url}\n错误: {e}", is_error=True)
    except Exception as e:
        return _tool_result(f"**调用失败**：{type(e).__name__}: {e}", is_error=True)


@mcp.tool()
def get_langgraph_status(change_id: str, base_url: str = DEFAULT_BASE) -> CallToolResult:
    """
    查询 LangGraph 后端某 change_id 的执行状态。

    - change_id: 变更 ID
    - base_url: 后端地址，默认 http://127.0.0.1:8000
    """
    url = f"{base_url.rstrip('/')}/status/{change_id}"
    try:
        res = _http_get(url)
        return _tool_result(json.dumps(res, ensure_ascii=False, indent=2))
    except urllib.error.URLError as e:
        return _tool_result(f"无法连接后端: {e}", is_error=True)
    except Exception as e:
        return _tool_result(f"{type(e).__name__}: {e}", is_error=True)


@mcp.tool()
def langgraph_health(base_url: str = DEFAULT_BASE) -> CallToolResult:
    """
    探测 LangGraph 后端健康状态。

    - base_url: 后端地址，默认 http://127.0.0.1:8000
    """
    url = f"{base_url.rstrip('/')}/health"
    try:
        res = _http_get(url)
        return _tool_result(json.dumps(res, ensure_ascii=False, indent=2))
    except urllib.error.URLError as e:
        return _tool_result(f"后端未就绪: {e}", is_error=True)
    except Exception as e:
        return _tool_result(f"{type(e).__name__}: {e}", is_error=True)


@mcp.tool()
def human_confirm_poll(
    change_id: str,
    timeout_seconds: int = 60,
    base_url: str = DEFAULT_BASE,
) -> CallToolResult:
    """
    Long Poll：在 timeout_seconds 内等待该 change_id 出现待人工确认项（如 Step 4.5/7.5）。
    前端可轮询此工具以实时收到「需要确认」通知。

    - change_id: 变更 ID
    - timeout_seconds: 最长等待秒数（1–120），默认 60
    - base_url: 后端地址，默认 http://127.0.0.1:8000
    """
    url = f"{base_url.rstrip('/')}/confirm/poll?change_id={change_id}&timeout_seconds={max(1, min(timeout_seconds, 120))}"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout_seconds + 5) as r:
            res = json.loads(r.read().decode("utf-8"))
        return _tool_result(json.dumps(res, ensure_ascii=False, indent=2))
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            body = str(e)
        return _tool_result(f"请求失败 HTTP {e.code}: {body}", is_error=True)
    except Exception as e:
        return _tool_result(f"{type(e).__name__}: {e}", is_error=True)


@mcp.tool()
def human_confirm_submit(
    change_id: str,
    request_id: str,
    decision: str,
    comment: str = "",
    reviewer: str = "",
    base_url: str = DEFAULT_BASE,
) -> CallToolResult:
    """
    提交人工确认结果（approve / reject / comment）。提交后需落盘对应 step4.5/step7.5 确认记录文件，再调用 run_langgraph 继续执行。

    - change_id: 变更 ID
    - request_id: 待确认项 ID（通常为 human_confirm_poll 返回的 request_id 或 run 返回的 thread_id）
    - decision: approve | reject | comment
    - comment: 可选备注
    - reviewer: 确认人标识
    - base_url: 后端地址，默认 http://127.0.0.1:8000
    """
    if decision not in ("approve", "reject", "comment"):
        return _tool_result("错误: decision 须为 approve | reject | comment", is_error=True)
    url = f"{base_url.rstrip('/')}/confirm/submit"
    try:
        body = {
            "change_id": change_id,
            "request_id": request_id,
            "decision": decision,
            "comment": comment or "",
            "reviewer": reviewer,
        }
        res = _http_post(url, body)
        return _tool_result(json.dumps(res, ensure_ascii=False, indent=2))
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            body = str(e)
        return _tool_result(f"提交失败 HTTP {e.code}: {body}", is_error=True)
    except Exception as e:
        return _tool_result(f"{type(e).__name__}: {e}", is_error=True)


if __name__ == "__main__":
    mcp.run(transport="stdio")
