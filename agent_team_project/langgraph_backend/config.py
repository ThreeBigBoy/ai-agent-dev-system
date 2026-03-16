"""配置加载与路径解析，供 parser / workflow / server 使用。"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

# 本包所在目录（agent_team_project/langgraph_backend）
PACKAGE_DIR = Path(__file__).resolve().parent
# agent_team_project 根
AGENT_TEAM_ROOT = PACKAGE_DIR.parent


# Phase 配置定义（阶段化执行架构）
# 格式: phase_id -> {description, task_patterns, max_latency_seconds, dependencies}
# task_patterns 可以是: ["1.1", "1.2"] 或 "1.*" 或 "all"
# 
# ⚠️ 注意：task_patterns 当前为硬编码，与 tasks.md 的任务编号对应。
# 若 tasks.md 结构变化，需同步更新此配置。
# TODO: 后续考虑从 tasks.md 的 phase 元信息（如注释 # phase: env-check）动态解析
DEFAULT_PHASES: dict[str, dict[str, Any]] = {
    "env-check": {
        "description": "环境自检",
        "task_patterns": ["1.1", "1.2", "1.3"],  # 环境检查相关任务（对应 tasks.md 1.1-1.3）
        "max_latency_seconds": 60,
        "dependencies": [],  # 无依赖
    },
    "mcp-check": {
        "description": "MCP 配置检查",
        "task_patterns": ["1.4", "1.5", "1.6"],  # MCP 配置相关任务（对应 tasks.md 1.4-1.6）
        "max_latency_seconds": 60,
        "dependencies": [],  # 可并行执行
    },
    "biz-trace": {
        "description": "业务留痕检查",
        "task_patterns": ["1.7"],  # 业务验证相关任务（对应 tasks.md 1.7）
        "max_latency_seconds": 300,
        "dependencies": [],  # 可独立执行
    },
    "full": {
        "description": "全量执行",
        "task_patterns": "all",  # 所有任务
        "max_latency_seconds": 600,
        "dependencies": [],
    },
}


def get_phase_config(phase: str | None) -> dict[str, Any] | None:
    """获取指定 phase 的配置。"""
    if phase is None:
        return DEFAULT_PHASES.get("full")
    return DEFAULT_PHASES.get(phase)


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
