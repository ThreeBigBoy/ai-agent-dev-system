#!/usr/bin/env python3
"""MCP server for agent-team: write_decision tool with JSON schema validation."""

import json
import os
import sys
from pathlib import Path

try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("Please install mcp: pip3 install mcp (or pip install mcp)", file=sys.stderr)
    sys.exit(1)

import jsonschema

from runtime_config import load_runtime_config


RUNTIME_CONFIG = load_runtime_config()
EXECUTORS = RUNTIME_CONFIG["executors"]
BASE_DIR = Path(__file__).resolve().parent

DECISION_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["task_complexity", "task_list"],
    "properties": {
        "task_complexity": {
            "type": "string",
            "enum": ["简单", "中等", "复杂"],
        },
        "matched_scene": {
            "type": "string",
            "enum": [
                "scene1-openspec-fullflow",
                "scene2-professional-agent",
                "scene3-other",
            ],
        },
        "reason": {
            "type": "string",
            "description": "一条自然语言理由，解释当前任务复杂度与场景判定原因",
        },
        "task_list": {
            "type": "array",
            "items": {
                "type": "object",
                "required": [
                    "task_id",
                    "task_name",
                    "executor",
                    "input_requirement",
                    "dependency",
                ],
                "properties": {
                    "task_id": {"type": "integer", "minimum": 1},
                    "task_name": {"type": "string"},
                    "executor": {
                        "type": "string",
                        "enum": EXECUTORS,
                    },
                    "input_requirement": {"type": "string"},
                    "dependency": {
                        "oneOf": [
                            {"type": "integer"},
                            {"type": "string"},
                        ]
                    },
                },
                "additionalProperties": False,
            },
        },
    },
    "additionalProperties": False,
}


def _project_root() -> Path:
    """Return project root where decision files should be written."""
    root = os.environ.get("AGENT_TEAM_PROJECT_ROOT", "").strip()
    if root and Path(root).is_dir():
        return Path(root)
    return Path.cwd()


def _decision_paths(root: Path) -> list[Path]:
    """写入决策文件路径（仅 agent_decision.json，V2.2 多宿主通用命名）."""
    paths = [root / "agent_decision.json"]
    if root != BASE_DIR:
        paths.append(BASE_DIR / "agent_decision.json")
    return paths


mcp = FastMCP("agent-team")  # description: "Agent team decision and state tools"


@mcp.tool()
def write_decision(decision: dict) -> dict:
    """
    Validate decision JSON and write decision files.

    Input:
      decision: {
        "task_complexity": "简单/中等/复杂",
        "matched_scene": "scene1-openspec-fullflow" | "scene2-professional-agent" | "scene3-other",  # 可选
        "reason": "<一条自然语言理由>",  # 可选，解释为何做出上述复杂度与场景判定
        "task_list": [
          {
            "task_id": int >= 1,
            "task_name": str,
            "executor": "默认 runtime backend 支持的 executor 之一",
            "input_requirement": str,
            "dependency": int or str
          }
        ]
      }

    Returns:
      { "ok": true, "path": "<abs path>" }
      or
      {
        "ok": false,
        "error_code": "...",
        "message": "...",
        "details": { ... }
      }
    """
    root = _project_root()
    paths = _decision_paths(root)

    if isinstance(decision, str):
        try:
            decision = json.loads(decision)
        except json.JSONDecodeError as e:
            return {
                "ok": False,
                "error_code": "JSON_PARSE_ERROR",
                "message": str(e),
                "details": {},
            }

    try:
        jsonschema.validate(instance=decision, schema=DECISION_SCHEMA)
    except jsonschema.ValidationError as e:
        return {
            "ok": False,
            "error_code": "VALIDATION_ERROR",
            "message": getattr(e, "message", str(e)),
            "details": {
                "json_path": list(e.absolute_path) if getattr(e, "absolute_path", None) else [],
                "schema_path": list(e.absolute_schema_path)
                if getattr(e, "absolute_schema_path", None)
                else [],
            },
        }
    except Exception as e:  # schema misconfiguration, etc.
        return {
            "ok": False,
            "error_code": "SCHEMA_ERROR",
            "message": str(e),
            "details": {},
        }

    try:
        for path in paths:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(decision, f, ensure_ascii=False, indent=2)
        return {"ok": True, "path": str(paths[0]), "compat_paths": [str(path) for path in paths[1:]]}
    except OSError as e:
        return {
            "ok": False,
            "error_code": "WRITE_ERROR",
            "message": str(e),
            "details": {"paths": [str(path) for path in paths]},
        }


if __name__ == "__main__":
    mcp.run(transport="stdio")
