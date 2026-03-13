#!/usr/bin/env python3
"""
Append a single model call record to runtime-logs/model-calls/YYYY-MM-DD.jsonl.

Usage example (from repo root):

  python3 scripts/runtime-logging/append_cursor_model_call.py \\
    --change-id sys-infra-memory-v1 \\
    --agent-role 主Agent \\
    --skill request-analysis \\
    --model-name auto

This script is intentionally minimal and host-agnostic:
- It does NOT call any external API.
- It only appends one JSON line with the fields defined in runtime-logs/README.md.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


def build_record(
    change_id: str,
    agent_role: str,
    skill: Optional[str],
    host: str,
    host_group: str,
    model_family: str,
    model_provider: str,
    model_name: Optional[str],
    metering_method: str,
    status: str,
    duration_ms: Optional[int],
    error_type: Optional[str],
    error_message: Optional[str],
) -> Dict[str, Any]:
  now = datetime.now().astimezone()

  error_info: Optional[Dict[str, str]] = None
  if error_type or error_message:
    error_info = {
      "type": error_type or "",
      "message": error_message or "",
    }

  record: Dict[str, Any] = {
    "timestamp": now.isoformat(timespec="seconds"),
    "change_id": change_id,
    "agent_role": agent_role,
    "skill": skill,
    "host": host,
    "host_group": host_group,
    "session_id": None,
    "model_family": model_family,
    "model_provider": model_provider,
    "model_name": model_name,
    "metering_method": metering_method,
    "tokens": {
      "prompt": None,
      "completion": None,
      "total": None,
    },
    "duration_ms": duration_ms,
    "status": status,
    "error_info": error_info,
  }

  return record


def append_record(record: Dict[str, Any]) -> Path:
  # scripts/runtime-logging/ -> repo root is parents[2]
  root = Path(__file__).resolve().parents[2]
  model_calls_dir = root / "runtime-logs" / "model-calls"
  model_calls_dir.mkdir(parents=True, exist_ok=True)

  file_name = datetime.now().strftime("%Y-%m-%d") + ".jsonl"
  file_path = model_calls_dir / file_name

  with file_path.open("a", encoding="utf-8") as f:
    json_line = json.dumps(record, ensure_ascii=False)
    f.write(json_line + "\n")

  return file_path


def parse_args() -> argparse.Namespace:
  parser = argparse.ArgumentParser(
    description="Append a model call record to runtime-logs/model-calls/*.jsonl",
  )
  parser.add_argument(
    "--change-id",
    required=True,
    help="The OpenSpec change-id this call belongs to (e.g. sys-infra-memory-v1).",
  )
  parser.add_argument(
    "--agent-role",
    default="主Agent",
    help="Agent role for this call (default: 主Agent).",
  )
  parser.add_argument(
    "--skill",
    default=None,
    help="Optional skill name associated with this call.",
  )
  parser.add_argument(
    "--model-name",
    default=None,
    help="Optional concrete model name if known (otherwise leave empty).",
  )
  parser.add_argument(
    "--host",
    default="cursor",
    help="Host identifier (e.g. cursor, vscode, continue, generic). Default: cursor.",
  )
  parser.add_argument(
    "--host-group",
    default="whitelist",
    help="Host group (e.g. whitelist, third_party, other). Default: whitelist.",
  )
  parser.add_argument(
    "--model-family",
    default="host_builtin_primary",
    help="Abstract model family (default: host_builtin_primary).",
  )
  parser.add_argument(
    "--model-provider",
    default="cursor_builtin",
    help="Model provider (e.g. cursor_builtin, vscode_builtin, openai_compatible, unknown). Default: cursor_builtin.",
  )
  parser.add_argument(
    "--status",
    default="success",
    choices=["success", "error", "rate_limited"],
    help="Call status (default: success).",
  )
  parser.add_argument(
    "--metering-method",
    default="none",
    choices=["none", "openai_usage", "cursor_usage_api", "estimation", "unknown"],
    help="Metering method for tokens/cost (default: none).",
  )
  parser.add_argument(
    "--duration-ms",
    type=int,
    default=None,
    help="Optional duration in milliseconds.",
  )
  parser.add_argument(
    "--error-type",
    default=None,
    help="Optional error type when status is not success.",
  )
  parser.add_argument(
    "--error-message",
    default=None,
    help="Optional error message (will be stored in a redacted form).",
  )

  return parser.parse_args()


def main() -> None:
  args = parse_args()
  record = build_record(
    change_id=args.change_id,
    agent_role=args.agent_role,
    skill=args.skill,
    host=args.host,
    host_group=args.host_group,
    model_family=args.model_family,
    model_provider=args.model_provider,
    model_name=args.model_name,
    metering_method=args.metering_method,
    status=args.status,
    duration_ms=args.duration_ms,
    error_type=args.error_type,
    error_message=args.error_message,
  )
  file_path = append_record(record)
  print(f"Appended model call record to {file_path}")


if __name__ == "__main__":
  main()

