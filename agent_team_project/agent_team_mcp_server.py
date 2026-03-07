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

DECISION_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["task_complexity", "task_list"],
    "properties": {
        "task_complexity": {
            "type": "string",
            "enum": ["简单", "中等", "复杂"],
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
    """Return project root where cursor_decision.json lives."""
    root = os.environ.get("AGENT_TEAM_PROJECT_ROOT", "").strip()
    if root and Path(root).is_dir():
        return Path(root)
    return Path.cwd()


mcp = FastMCP("agent-team")  # description: "Agent team decision and state tools"


@mcp.tool()
def write_decision(decision: dict) -> dict:
    """
    Validate decision JSON and write cursor_decision.json.

    Input:
      decision: {
        "task_complexity": "简单/中等/复杂",
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
    path = root / "cursor_decision.json"

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
        with open(path, "w", encoding="utf-8") as f:
            json.dump(decision, f, ensure_ascii=False, indent=2)
        return {"ok": True, "path": str(path)}
    except OSError as e:
        return {
            "ok": False,
            "error_code": "WRITE_ERROR",
            "message": str(e),
            "details": {"path": str(path)},
        }


if __name__ == "__main__":
    mcp.run(transport="stdio")
