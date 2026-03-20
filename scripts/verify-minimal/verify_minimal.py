#!/usr/bin/env python3
"""
最小验证脚本：从头到尾人工验证 LangGraph 管线（V2.11.1）。

从 ai-agent-dev-system 仓库根执行：
  python scripts/verify-minimal/verify_minimal.py [--workspace /path/to/repo] [--skip-http]

步骤：
  1. 运行 diagnose_startup.py（环境与配置检查）
  2. 本地 invoke workflow：无 HC0 确认文件 → 应得到 status=waiting_hc0
  3. 若有 HC0 确认文件则再 invoke 一次 → 应得到 status=waiting_hc7（或 done，若已有 HC7 确认文件）
  4. 若未加 --skip-http 且后端已启动，则请求 GET /health 与 GET /confirm/pending（可选）

退出码：0 表示全部通过，非 0 表示有步骤失败。
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def _repo_root(workspace: Path | None) -> Path:
    root = workspace or Path.cwd()
    root = root.resolve()
    if not (root / "openspec").is_dir():
        # 可能当前在 agent_team_project 或子目录
        for p in [root.parent, root.parent.parent]:
            if (p / "openspec").is_dir():
                return p
    return root


def run_diagnose(root: Path) -> bool:
    """执行 diagnose_startup.py，返回是否通过（healthy 或 仅 network 失败视为可接受）。"""
    script = root / "scripts" / "diagnose_startup" / "diagnose_startup.py"
    if not script.exists():
        print("[FAIL] scripts/diagnose_startup/diagnose_startup.py 不存在")
        return False
    out = subprocess.run(
        [sys.executable, str(script), "--workspace", str(root)],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(root),
    )
    if out.returncode != 0:
        # 若仅因 network 不通过（后端未启），仍算通过
        if "network-connectivity" in (out.stdout or "") or "Connection refused" in (out.stderr or ""):
            print("[OK] 诊断脚本已执行（network 未通过为预期，需先启动后端）")
            return True
        print("[FAIL] 诊断脚本返回非 0:", out.stderr or out.stdout)
        return False
    print("[OK] 诊断脚本通过")
    return True


def run_workflow_scenario_a(root: Path, change_id: str) -> bool:
    """场景 A：无 HC0 文件 → 应得到 waiting_hc0。"""
    # 确保无 HC0 确认文件
    records = root / "design" / "documents" / "changes" / change_id / "records"
    hc0_file = records / f"{change_id}-step0.5-clarification-confirmation.md"
    had_file = hc0_file.exists()
    if had_file:
        try:
            hc0_file.rename(records / f"{change_id}-step0.5-clarification-confirmation.md.bak")
        except Exception:
            pass
    try:
        sys.path.insert(0, str(root / "agent_team_project"))
        os.environ["AGENT_TEAM_PROJECT_ROOT"] = str(root)
        from langgraph_backend.workflow import get_graph

        g = get_graph()
        initial = {
            "change_id": change_id,
            "task_range": None,
            "phase": "full",
            "decision": {},
            "results": [],
            "feedback": "",
            "status": "pending",
            "ckpt_ref": None,
            "workspace_root": str(root),
            "project_key": None,
            "workspace_projects": None,
            "resolved_workspace_root": None,
            "resolved_project_key": None,
            "human_confirmed": None,
            "human_confirm_step": None,
            "step0_output": None,
            "step0_skip": None,
            "step0_retry": None,
            "step0_completed": None,
        }
        config = {"configurable": {"thread_id": "verify-minimal-a"}}
        final = g.invoke(initial, config=config)
        status = final.get("status")
        if status != "waiting_hc0":
            print(f"[FAIL] 场景 A 期望 status=waiting_hc0，实际={status}")
            return False
        print("[OK] 场景 A：无 HC0 文件 → status=waiting_hc0")
        return True
    except Exception as e:
        print(f"[FAIL] 场景 A 异常: {e}")
        return False
    finally:
        if had_file and records.exists():
            bak = records / f"{change_id}-step0.5-clarification-confirmation.md.bak"
            if bak.exists():
                try:
                    bak.rename(hc0_file)
                except Exception:
                    pass
        if "langgraph_backend.workflow" in sys.modules:
            sys.modules.pop("langgraph_backend.workflow", None)
        if "langgraph_backend" in sys.modules:
            for k in list(sys.modules):
                if k.startswith("langgraph_backend"):
                    sys.modules.pop(k, None)


def run_workflow_scenario_b(root: Path, change_id: str) -> bool:
    """场景 B：有 HC0 文件 → 应得到 waiting_hc7 或 done。"""
    records = root / "design" / "documents" / "changes" / change_id / "records"
    hc0_file = records / f"{change_id}-step0.5-clarification-confirmation.md"
    if not hc0_file.exists():
        # 创建临时 HC0 确认文件
        records.mkdir(parents=True, exist_ok=True)
        hc0_file.write_text("# Step 0.5 确认（verify_minimal 用）\n", encoding="utf-8")
        created = True
    else:
        created = False
    try:
        if "AGENT_TEAM_PROJECT_ROOT" not in os.environ:
            os.environ["AGENT_TEAM_PROJECT_ROOT"] = str(root)
        if str(root / "agent_team_project") not in sys.path:
            sys.path.insert(0, str(root / "agent_team_project"))
        from langgraph_backend.workflow import get_graph

        g = get_graph()
        initial = {
            "change_id": change_id,
            "task_range": None,
            "phase": "full",
            "decision": {},
            "results": [],
            "feedback": "",
            "status": "pending",
            "ckpt_ref": None,
            "workspace_root": str(root),
            "project_key": None,
            "workspace_projects": None,
            "resolved_workspace_root": None,
            "resolved_project_key": None,
            "human_confirmed": None,
            "human_confirm_step": None,
            "step0_output": None,
            "step0_skip": None,
            "step0_retry": None,
            "step0_completed": None,
        }
        config = {"configurable": {"thread_id": "verify-minimal-b"}}
        final = g.invoke(initial, config=config)
        status = final.get("status")
        if status not in ("waiting_hc7", "done"):
            print(f"[FAIL] 场景 B 期望 status=waiting_hc7 或 done，实际={status}")
            return False
        print(f"[OK] 场景 B：有 HC0 文件 → status={status}")
        return True
    except Exception as e:
        print(f"[FAIL] 场景 B 异常: {e}")
        return False
    finally:
        if created and hc0_file.exists():
            try:
                hc0_file.unlink()
            except Exception:
                pass


def run_http_checks(base_url: str) -> bool:
    """可选：GET /health 与 GET /confirm/pending。"""
    try:
        import json
        import urllib.request
        import urllib.error

        req = urllib.request.Request(f"{base_url.rstrip('/')}/health", method="GET")
        with urllib.request.urlopen(req, timeout=5) as r:
            data = json.loads(r.read().decode())
        if data.get("status") != "healthy":
            print(f"[FAIL] /health 返回 status={data.get('status')}")
            return False
        print("[OK] GET /health 通过")
        req2 = urllib.request.Request(
            f"{base_url}/confirm/pending?change_id=deepen-langgraph-v2-11-1",
            method="GET",
        )
        try:
            with urllib.request.urlopen(req2, timeout=3) as r2:
                json.loads(r2.read().decode())
            print("[OK] GET /confirm/pending 返回 200（有待确认项时）")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                print("[OK] GET /confirm/pending 返回 404（当前无待确认项，符合预期）")
            else:
                print(f"[WARN] GET /confirm/pending 返回 {e.code}")
        return True
    except Exception as e:
        print(f"[WARN] HTTP 检查跳过或失败: {e}")
        return True  # 不阻塞整体


def main() -> int:
    parser = argparse.ArgumentParser(description="最小验证脚本（V2.11.1 管线）")
    parser.add_argument("--workspace", type=Path, default=None, help="仓库根目录，默认 cwd")
    parser.add_argument("--skip-http", action="store_true", help="跳过 HTTP /health 与 /confirm/pending 检查")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="后端 base URL（用于 HTTP 检查）")
    parser.add_argument("--change-id", default="deepen-langgraph-v2-11-1", help="用于验证的 change_id")
    args = parser.parse_args()

    root = _repo_root(args.workspace)
    if not (root / "openspec").is_dir():
        print("[FAIL] 未找到仓库根（无 openspec 目录）")
        return 1
    os.environ["AGENT_TEAM_PROJECT_ROOT"] = str(root)
    print("仓库根:", root)
    print("---")

    ok = True
    if not run_diagnose(root):
        ok = False
    if not run_workflow_scenario_a(root, args.change_id):
        ok = False
    if not run_workflow_scenario_b(root, args.change_id):
        ok = False
    if not args.skip_http and not run_http_checks(args.base_url):
        ok = False

    print("---")
    if ok:
        print("全部通过。")
        return 0
    print("存在失败项，请检查上述输出。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
