"""配置加载与路径解析，供 parser / workflow / server 使用。"""
from __future__ import annotations

import os
from pathlib import Path

# 本包所在目录（agent_team_project/langgraph_backend）
PACKAGE_DIR = Path(__file__).resolve().parent
# agent_team_project 根
AGENT_TEAM_ROOT = PACKAGE_DIR.parent


def get_workspace_root() -> Path | None:
    """openspec 所在仓库根目录。"""
    root = os.environ.get("AGENT_TEAM_PROJECT_ROOT", "").strip()
    if root and Path(root).is_dir():
        return Path(root)
    # 默认假设 agent_team_project 在 ai-agent-dev-system/agent_team_project
    candidate = AGENT_TEAM_ROOT.parent
    if (candidate / "openspec").is_dir():
        return candidate
    return None


def get_openspec_changes_dir() -> Path | None:
    """openspec/changes 目录（默认：AGENT_TEAM_PROJECT_ROOT 指向的仓库，即 ai-agent-dev-system）。"""
    root = get_workspace_root()
    if root is None:
        return None
    d = root / "openspec" / "changes"
    return d if d.is_dir() else None


def get_openspec_changes_dir_for(project_root: Path) -> Path | None:
    """指定项目根下的 openspec/changes 目录（用于业务项目，如 Proj01ShopifyTheme）。"""
    if not project_root.is_dir():
        return None
    d = project_root / "openspec" / "changes"
    return d if d.is_dir() else None


def get_runtime_logs_root() -> Path | None:
    """ai-agent-dev-system 的 runtime-logs 根目录（留痕统一写在此处，与执行时用哪个 project 无关）。"""
    root = get_workspace_root()
    if root is None:
        return None
    logs = root / "runtime-logs"
    return logs if logs.is_dir() else None
