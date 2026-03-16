#!/usr/bin/env python3
"""
LangGraph 后端一键自检脚本（change-id: check-langgraph-backend）

自动执行：
1. GET /health 判定 healthy
2. 检查 AGENT_TEAM_PROJECT_ROOT 是否指向 ai-agent-dev-system
3. 从 ~/.cursor/mcp.json 解析 LANGGRAPH_WORKSPACE_PROJECTS，逐项验证目录存在
4. 本仓 change-id 执行一次 /run，检查 runtime-logs/langgraph-runs 是否有对应记录
5. 业务项目 change-id 执行一次 /run，检查留痕是否含 project_key/workspace_root

用法（在仓库根或任意处）：
  python scripts/check-langgraph-backend/check_langgraph_backend.py [--base-url URL] [--skip-run]
  --base-url  默认 http://127.0.0.1:8000
  --skip-run  只做 1～3 项，不执行 /run 与留痕检查
  --no-prompt 不询问 change-id，使用默认或命令行参数（非交互/CI 时用）

在交互式终端下（未加 --no-prompt 时），脚本会先询问本仓 change-id、业务项目 change-id；
直接回车使用默认值，输入 skip 可跳过第 5 项业务项目 /run。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

DEFAULT_BASE = "http://127.0.0.1:8000"
MCP_JSON_PATH = Path.home() / ".cursor" / "mcp.json"
# 本仓 change-id 默认值（用于自检；若已归档可传 --local-change-id 指定仍存在的）
DEFAULT_LOCAL_CHANGE_ID = "check-langgraph-backend"
# 业务项目示例（可被 --workspace-projects / --business-change-id 覆盖）
DEFAULT_WORKSPACE_PROJECTS = "Proj01ShopifyTheme|/Users/billhu/Cursor Projects/Proj01ShopifyTheme:test_bizproject|/Users/billhu/Cursor Projects/test_bizproject"
DEFAULT_BUSINESS_CHANGE_ID = "2026-03-14-update-theme-v1.0.2-mvp-health-compliance"


def _script_repo_root() -> Path:
    """脚本位于 scripts/check-langgraph-backend/ -> 仓库根 = 上两级."""
    return Path(__file__).resolve().parent.parent.parent


def _get_agent_team_root() -> Path | None:
    root = os.environ.get("AGENT_TEAM_PROJECT_ROOT", "").strip()
    if root and Path(root).is_dir():
        return Path(root)
    return None


def _resolve_repo_root_for_logs() -> Path:
    """
    用于写 runtime-logs 的仓库根解析策略：
    - 优先使用 AGENT_TEAM_PROJECT_ROOT（允许指向 ai-agent-dev-system 或 agent_team_project）
    - 否则回退到脚本所在路径推断的仓库根
    """
    root = _get_agent_team_root()
    if root is None:
        return _script_repo_root()
    if (root / "runtime-logs").is_dir():
        return root
    if root.name == "agent_team_project" and (root.parent / "runtime-logs").is_dir():
        return root.parent
    return _script_repo_root()


def _append_system_event(line: str) -> None:
    """追加一条系统事件留痕到 runtime-logs/system-events/events.log。"""
    repo_root = _resolve_repo_root_for_logs()
    out_dir = repo_root / "runtime-logs" / "system-events"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "events.log"
    out_file.write_text("", encoding="utf-8") if not out_file.exists() else None
    with out_file.open("a", encoding="utf-8") as f:
        f.write(line.rstrip("\n") + "\n")


def check_health(base_url: str) -> tuple[bool, str]:
    try:
        req = urllib.request.Request(f"{base_url.rstrip('/')}/health", method="GET")
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read().decode("utf-8"))
        if data.get("status") == "healthy":
            return True, "GET /health: healthy"
        return False, f"GET /health: status={data.get('status')}"
    except urllib.error.URLError as e:
        return False, f"GET /health 请求失败: {e}"
    except Exception as e:
        return False, f"GET /health: {e}"


def check_agent_team_project_root() -> tuple[bool, str]:
    root = _get_agent_team_root()
    if root is None:
        return False, "AGENT_TEAM_PROJECT_ROOT 未设置；请 export 指向 ai-agent-dev-system 或 agent_team_project 所在目录"
    # 允许指向 agent_team_project 或 ai-agent-dev-system
    openspec_in_root = (root / "openspec" / "changes").is_dir()
    parent_openspec = (root.parent / "openspec" / "changes").is_dir()
    if openspec_in_root or parent_openspec:
        return True, f"AGENT_TEAM_PROJECT_ROOT 已设置且含 openspec/changes: {root}"
    return False, f"AGENT_TEAM_PROJECT_ROOT={root} 下未发现 openspec/changes（本仓根应为 ai-agent-dev-system）"


def _parse_workspace_projects_from_mcp(raw: str) -> list[tuple[str, str]]:
    """解析 LANGGRAPH_WORKSPACE_PROJECTS 为 [(key, path), ...]."""
    raw = (raw or "").strip()
    if not raw:
        return []
    if raw.startswith("["):
        try:
            arr = json.loads(raw)
            if not isinstance(arr, list):
                return []
            pairs = []
            for item in arr:
                if isinstance(item, dict):
                    k = (item.get("LANGGRAPH_PROJECT_KEY") or item.get("project_key") or "").strip()
                    r = (item.get("LANGGRAPH_WORKSPACE_ROOT") or item.get("workspace_root") or "").strip()
                    if k and r:
                        pairs.append((k, r))
            return pairs
        except (json.JSONDecodeError, TypeError):
            pass
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
    return pairs


def get_workspace_projects_from_mcp() -> tuple[list[tuple[str, str]], str]:
    """从 ~/.cursor/mcp.json 读取 LANGGRAPH_WORKSPACE_PROJECTS，返回 (pairs, raw_flat) 供第 5 项使用；raw_flat 为 key|path:key2|path2 格式."""
    if not MCP_JSON_PATH.is_file():
        return [], ""
    try:
        data = json.loads(MCP_JSON_PATH.read_text(encoding="utf-8"))
    except Exception:
        return [], ""
    servers = data.get("mcpServers") or {}
    backend = servers.get("langgraph-backend") or {}
    env = backend.get("env") or {}
    raw = (env.get("LANGGRAPH_WORKSPACE_PROJECTS") or "").strip()
    pairs = _parse_workspace_projects_from_mcp(raw)
    flat = ":".join(f"{k}|{p}" for k, p in pairs) if pairs else ""
    return pairs, flat


def check_workspace_projects_dirs() -> tuple[bool, str]:
    pairs, _ = get_workspace_projects_from_mcp()
    if not pairs:
        return True, "~/.cursor/mcp.json 不存在或 LANGGRAPH_WORKSPACE_PROJECTS 未配置，跳过目录校验"
    missing = [path for _, path in pairs if not Path(path).is_dir()]
    if missing:
        return False, f"LANGGRAPH_WORKSPACE_PROJECTS 中以下路径不存在: {missing}"
    return True, f"LANGGRAPH_WORKSPACE_PROJECTS 共 {len(pairs)} 项，目录均存在"


def post_run(base_url: str, change_id: str, workspace_projects: str | None = None, phase: str | None = None, timeout: int = 120) -> tuple[bool, str, dict]:
    """执行 /run，支持阶段化执行（phase 参数）。"""
    url = f"{base_url.rstrip('/')}/run"
    body: dict = {"change_id": change_id}
    if workspace_projects:
        body["workspace_projects"] = workspace_projects
    if phase:
        body["phase"] = phase
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read().decode("utf-8"))
        return True, f"POST /run (phase={phase or 'full'}) 成功", data
    except urllib.error.HTTPError as e:
        body_str = e.read().decode("utf-8", errors="replace") if e.fp else ""
        return False, f"POST /run (phase={phase or 'full'}) HTTP {e.code}: {body_str}", {}
    except Exception as e:
        return False, f"POST /run (phase={phase or 'full'}): {e}", {}


def get_runtime_logs_root() -> Path | None:
    root = _get_agent_team_root()
    if root is None:
        root = _script_repo_root()
    # runtime-logs 在 ai-agent-dev-system 根下；若 root 为 agent_team_project 则用其父目录
    if root.name == "agent_team_project" and (root.parent / "runtime-logs").is_dir():
        repo_root = root.parent
    else:
        repo_root = root
    logs = repo_root / "runtime-logs" / "langgraph-runs"
    return logs if logs.is_dir() else None


def today_jsonl_path() -> Path | None:
    from datetime import datetime, timezone
    logs = get_runtime_logs_root()
    if not logs:
        return None
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    p = logs / f"{today}.jsonl"
    return p if p.is_file() else None


def count_recent_run_logs(change_id: str, after_ts: float | None = None) -> int:
    path = today_jsonl_path()
    if not path:
        return 0
    n = 0
    for line in path.read_text(encoding="utf-8").strip().splitlines():
        if not line:
            continue
        try:
            obj = json.loads(line)
            if obj.get("change_id") != change_id:
                continue
            if after_ts is not None and obj.get("ts"):
                # 简单比较时间字符串或时间戳
                n += 1
                continue
            n += 1
        except Exception:
            continue
    return n


def check_local_run_with_phases(base_url: str, local_change_id: str) -> tuple[bool, str, list[dict]]:
    """
    重构后的本仓 /run 检查：多次短调用（按 phase）+ 聚合。
    阶段：env-check → mcp-check → biz-trace（可选）
    """
    phases = [
        ("env-check", 60),   # (phase_name, timeout_seconds)
        ("mcp-check", 60),
        ("biz-trace", 120),  # 可选，较重
    ]
    
    results: list[dict] = []
    all_ok = True
    
    for phase, timeout in phases:
        ok, msg, data = post_run(base_url, local_change_id, workspace_projects=None, phase=phase, timeout=timeout)
        result = {
            "phase": phase,
            "ok": ok,
            "message": msg,
            "data": data,
            "latency_seconds": data.get("latency_seconds", 0) if data else 0,
        }
        results.append(result)
        if not ok:
            all_ok = False
            # 继续执行其他 phase，但标记失败
    
    # 检查留痕（简化：检查是否有任意 phase 的日志）
    log_count = count_recent_run_logs(local_change_id)
    has_logs = log_count > 0
    
    if not has_logs:
        all_ok = False
    
    # 生成聚合报告
    report_lines = [f"本仓 /run (change_id={local_change_id}) 阶段化执行结果："]
    for r in results:
        status = "✓" if r["ok"] else "✗"
        report_lines.append(f"  [{status}] {r['phase']}: {r['message']} (耗时: {r['latency_seconds']:.2f}s)")
    
    if not has_logs:
        report_lines.append("  ✗ 未在 runtime-logs 中发现留痕记录")
    else:
        report_lines.append(f"  ✓ 留痕已写入 (共 {log_count} 条记录)")
    
    summary = "\n".join(report_lines)
    return all_ok, summary, results


# 保持向后兼容的别名
def check_local_run_and_log(base_url: str, local_change_id: str) -> tuple[bool, str]:
    """向后兼容的包装函数。"""
    ok, summary, _ = check_local_run_with_phases(base_url, local_change_id)
    # 简化输出，保持原有格式
    if ok:
        return True, f"本仓 /run 成功且留痕已写入 (change_id={local_change_id}, 阶段化执行)"
    else:
        return False, f"本仓 /run 失败 (change_id={local_change_id})"



def check_business_run_with_phases(base_url: str, workspace_projects: str, business_change_id: str) -> tuple[bool, str, list[dict]]:
    """
    重构后的业务项目 /run 检查：多次短调用（按 phase）+ 聚合。
    阶段：env-check → mcp-check → biz-trace（可选）
    """
    phases = [
        ("env-check", 60),   # (phase_name, timeout_seconds)
        ("mcp-check", 60),
        # biz-trace 可选，视业务项目情况而定
    ]
    
    results: list[dict] = []
    all_ok = True
    
    for phase, timeout in phases:
        ok, msg, data = post_run(base_url, business_change_id, workspace_projects=workspace_projects, phase=phase, timeout=timeout)
        result = {
            "phase": phase,
            "ok": ok,
            "message": msg,
            "data": data,
            "latency_seconds": data.get("latency_seconds", 0) if data else 0,
        }
        results.append(result)
        if not ok:
            all_ok = False
    
    # 检查留痕
    log_count = count_recent_run_logs(business_change_id)
    has_logs = log_count > 0
    
    if not has_logs:
        all_ok = False
    
    # 生成聚合报告
    report_lines = [f"业务项目 /run (change_id={business_change_id}) 阶段化执行结果："]
    for r in results:
        status = "✓" if r["ok"] else "✗"
        report_lines.append(f"  [{status}] {r['phase']}: {r['message']} (耗时: {r['latency_seconds']:.2f}s)")
    
    if not has_logs:
        report_lines.append("  ✗ 未在 runtime-logs 中发现留痕记录")
    else:
        report_lines.append(f"  ✓ 留痕已写入 (共 {log_count} 条记录)")
    
    summary = "\n".join(report_lines)
    return all_ok, summary, results


# 保持向后兼容的别名
def check_business_run_and_log(base_url: str, workspace_projects: str, business_change_id: str) -> tuple[bool, str]:
    """向后兼容的包装函数。"""
    ok, summary, _ = check_business_run_with_phases(base_url, workspace_projects, business_change_id)
    # 简化输出，保持原有格式
    if ok:
        return True, f"业务项目 /run 成功且留痕已写入 (change_id={business_change_id}, 阶段化执行)"
    else:
        return False, f"业务项目 /run 失败 (change_id={business_change_id})"



def _prompt_change_ids(args: argparse.Namespace) -> None:
    """在交互式终端下询问本仓/业务 change-id，用户可直接回车用默认或输入新值。

    - 当传入 --skip-run 时，不询问（因为不会执行 /run）
    - 当传入 --local-only 时，只询问本仓 change-id，不询问业务项目 change-id
    - 当传入 --business-only 时，只询问业务项目 change-id，不询问本仓 change-id
    - 若命令行已显式传入 --local-change-id / --business-change-id，则对应项不再重复询问
    """
    if not sys.stdin.isatty():
        return
    if args.skip_run:
        return

    # 仅本仓模式：只问本仓 change-id
    if getattr(args, "local_only", False):
        if "--local-change-id" not in sys.argv:
            s = input(f"本仓 change-id [默认: {args.local_change_id}]: ").strip()
            if s:
                args.local_change_id = s
        return

    # 仅业务项目模式：只问业务项目 change-id（前提是存在 workspace_projects 配置）
    if getattr(args, "business_only", False):
        wp_pairs, wp_flat = get_workspace_projects_from_mcp()
        wp_for_run = wp_flat if wp_flat else (args.workspace_projects or "").strip()
        if wp_for_run:
            if "--business-change-id" not in sys.argv:
                s = input(
                    f"业务项目 change-id [默认: {args.business_change_id}，输入 skip 跳过第 5 项]: "
                ).strip()
                if s.lower() == "skip":
                    args._skip_business_run = True
                elif s:
                    args.business_change_id = s
        return

    # 默认：本仓 + 业务项目均可询问
    if "--local-change-id" not in sys.argv:
        s = input(f"本仓 change-id [默认: {args.local_change_id}]: ").strip()
        if s:
            args.local_change_id = s
    wp_pairs, wp_flat = get_workspace_projects_from_mcp()
    wp_for_run = wp_flat if wp_flat else (args.workspace_projects or "").strip()
    if wp_for_run:
        if "--business-change-id" not in sys.argv:
            s = input(
                f"业务项目 change-id [默认: {args.business_change_id}，输入 skip 跳过第 5 项]: "
            ).strip()
            if s.lower() == "skip":
                args._skip_business_run = True
            elif s:
                args.business_change_id = s


def main() -> int:
    ap = argparse.ArgumentParser(description="LangGraph 后端一键自检")
    ap.add_argument("--base-url", default=DEFAULT_BASE, help="后端 base URL")
    ap.add_argument(
        "--skip-run",
        action="store_true",
        help="只执行 1～3 项，不执行 /run 与留痕检查",
    )
    ap.add_argument(
        "--local-only",
        action="store_true",
        help="只验证本仓（执行 1/2/4），完全忽略 LANGGRAPH_WORKSPACE_PROJECTS 与业务项目 /run",
    )
    ap.add_argument(
        "--business-only",
        action="store_true",
        help="只验证业务项目（执行 1/2/3/5），不执行本仓 /run（第 4 项）",
    )
    ap.add_argument("--workspace-projects", default=DEFAULT_WORKSPACE_PROJECTS, help="业务项目 workspace_projects 串（用于第 5 项）")
    ap.add_argument("--local-change-id", default=DEFAULT_LOCAL_CHANGE_ID, help="本仓 change-id（第 4 项），需在本仓 openspec/changes 或 archive 下存在 tasks.md")
    ap.add_argument("--business-change-id", default=DEFAULT_BUSINESS_CHANGE_ID, help="业务项目 change-id（第 5 项）")
    ap.add_argument("--no-prompt", action="store_true", help="不询问 change-id，始终使用默认或命令行参数（非交互式或 CI 时使用）")
    args = ap.parse_args()
    base_url = args.base_url.rstrip("/")
    failed: list[str] = []
    skipped: list[str] = []

    # 交互式询问 change-id（仅当未传 --no-prompt 且为 TTY 时）
    if not getattr(args, "no_prompt", False):
        _prompt_change_ids(args)

    # 1. GET /health
    ok, msg = check_health(base_url)
    print(f"[{'PASS' if ok else 'FAIL'}] 1. {msg}")
    if not ok:
        failed.append("1. GET /health")

    # 2. AGENT_TEAM_PROJECT_ROOT
    ok, msg = check_agent_team_project_root()
    print(f"[{'PASS' if ok else 'FAIL'}] 2. {msg}")
    if not ok:
        failed.append("2. AGENT_TEAM_PROJECT_ROOT")

    # 3. LANGGRAPH_WORKSPACE_PROJECTS 解析与目录存在
    if args.local_only:
        print("[SKIP] 3. 本次仅验证本仓（--local-only），跳过 LANGGRAPH_WORKSPACE_PROJECTS 目录校验")
        skipped.append("3. LANGGRAPH_WORKSPACE_PROJECTS 目录校验")
        ok = True
    else:
        ok, msg = check_workspace_projects_dirs()
        print(f"[{'PASS' if ok else 'FAIL'}] 3. {msg}")
    if not ok:
        failed.append("3. LANGGRAPH_WORKSPACE_PROJECTS 目录校验")

    if args.skip_run:
        if failed:
            print("\n自检未通过:", ", ".join(failed))
            return 1
        print("\n自检通过（已跳过 /run 与留痕检查）")
        return 0

    # 4. 本仓 /run + 留痕
    if args.business_only:
        print("[SKIP] 4. 本次仅验证业务项目（--business-only），跳过本仓 /run 与留痕检查")
        skipped.append("4. 本仓 /run 或留痕")
    else:
        ok, msg = check_local_run_and_log(base_url, args.local_change_id)
        print(f"[{'PASS' if ok else 'FAIL'}] 4. {msg}")
        if not ok:
            failed.append("4. 本仓 /run 或留痕")

    # 5. 业务项目 /run + 留痕
    if args.local_only:
        print("[SKIP] 5. 本次仅验证本仓（--local-only），跳过业务项目 /run 与留痕检查")
        skipped.append("5. 业务项目 /run 或留痕")
    else:
        # 若 mcp 中无 LANGGRAPH_WORKSPACE_PROJECTS 则用命令行参数，若两者皆无或用户选择 skip 则跳过
        wp_pairs, wp_flat = get_workspace_projects_from_mcp()
        wp_for_run = wp_flat if wp_flat else (args.workspace_projects or "")
        if getattr(args, "_skip_business_run", False):
            wp_for_run = ""
        if not wp_for_run:
            print("[SKIP] 5. 未配置 LANGGRAPH_WORKSPACE_PROJECTS 且未传 --workspace-projects，或已选择跳过；跳过业务项目 /run")
            skipped.append("5. 业务项目 /run 或留痕")
        else:
            ok, msg = check_business_run_and_log(base_url, wp_for_run, args.business_change_id)
            print(f"[{'PASS' if ok else 'FAIL'}] 5. {msg}")
            if not ok:
                failed.append("5. 业务项目 /run 或留痕")

    if failed:
        print("\n自检未通过:", ", ".join(failed))
        return 1
    print("\n全部自检通过")
    return 0


if __name__ == "__main__":
    start = datetime.now()
    exit_code = 1
    failed_items: list[str] = []
    skipped_items: list[str] = []
    try:
        # 复用 main 的输出，但为了留痕更可控，这里直接运行 main 再补充留痕
        exit_code = main()
        # main 内部不暴露 failed/skipped；留痕以 exit_code + 参数为主，失败项用户可从终端输出回看
    except Exception as e:
        exit_code = 2
        failed_items = ["exception"]
        _append_system_event(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ERROR - script_run check-langgraph-backend: exception={type(e).__name__}: {e}"
        )
        raise
    finally:
        end = datetime.now()
        duration_ms = int((end - start).total_seconds() * 1000)
        # system-events 留痕：不记录敏感正文，仅记录元数据与退出码
        _append_system_event(
            f"[{end.strftime('%Y-%m-%d %H:%M:%S')}] INFO  - script_run check-langgraph-backend: "
            f"script=scripts/check-langgraph-backend/check_langgraph_backend.py, "
            f"exit_code={exit_code}, duration_ms={duration_ms}, "
            f"note='see terminal output for failed items if any'"
        )
    sys.exit(exit_code)
