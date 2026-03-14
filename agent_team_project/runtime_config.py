#!/usr/bin/env python3
"""Shared runtime backend configuration for agent_team_project."""

from __future__ import annotations

import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "runtime_config.json"

DEFAULT_CONFIG = {
    "backend_name": "inline-langgraph",
    "executors": [
        "产品经理",
        "架构师",
        "前端工程师",
        "后端工程师",
        "测试工程师",
        "文档 Agent",
        "Bug 修复 Agent",
    ],
    "host_policy": {
        "default_host": "cursor",
        "builtin_preferred_hosts": [
            "cursor",
            "vscode",
            "openai-codex",
        ],
        "api_preferred_hosts": [
            "continue",
        ],
        "subagent_provider_policy": {
            "default": "builtin_first",
            "builtin_first_hosts": [
                "cursor",
                "vscode",
                "openai-codex",
            ],
            "api_first_hosts": [
                "continue",
            ],
        },
    },
    "model_strategy": {
        "preferred_provider": "cursor_builtin",
        "fallback_provider": "api",
        "cursor_builtin": {
            "enabled": True,
            "mode": "Auto",
        },
        "api": {
            "enabled": True,
            "models": {
                "simple": [
                    "Qwen/Qwen3-8B",
                    "Pro/deepseek-ai/DeepSeek-V3.2",
                ],
                "complex": [
                    "Pro/deepseek-ai/DeepSeek-V3.2",
                    "Pro/MiniMaxAI/MiniMax-M2.5",
                    "Pro/moonshotai/Kimi-K2.5",
                ],
            },
        },
    },
    "llm": {
        "temperature": 0.1,
        "timeout_seconds": 60,
    },
    "run_skill": {
        "timeout_seconds": 300,
    },
}


def load_runtime_config() -> dict:
    """Load backend runtime config, falling back to defaults when needed."""
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            loaded = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        loaded = {}

    config = json.loads(json.dumps(DEFAULT_CONFIG, ensure_ascii=False))
    for section, value in loaded.items():
        if isinstance(value, dict) and isinstance(config.get(section), dict):
            config[section].update(value)
        else:
            config[section] = value
    return config
