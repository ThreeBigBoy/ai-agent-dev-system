#!/usr/bin/env python3
"""
Create a new memory entry file under memory/*/ with frontmatter and a minimal body skeleton.

Usage example (from repo root):

  python3 scripts/memory/create_memory_entry.py \
    --type pattern \
    --title "OpenSpec 变更标准流程（最小实践）" \
    --change-id sys-infra-memory-v1 \
    --tags openspec,change-flow \
    --applicable-projects ai-agent-dev-system \
    --host-scope cursor,vscode

The script will:
- Determine the target directory by type (patterns/anti-patterns/preferences/playbooks/reflections).
- Generate an id if not provided.
- Write a new Markdown file with YAML frontmatter following memory/schema.md
  and a minimal section skeleton for the given type.
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
from typing import List


TYPE_TO_SUBDIR = {
  "pattern": "patterns",
  "anti-pattern": "anti-patterns",
  "preference": "preferences",
  "playbook": "playbooks",
  "reflection": "reflections",
}


def parse_comma_list(value: str) -> List[str]:
  items = [v.strip() for v in value.split(",") if v.strip()]
  return items


def generate_id(mem_type: str, title: str) -> str:
  now = datetime.now()
  ts = now.strftime("%Y%m%d-%H%M%S")
  # simple, readable id; title part is optional and sanitized lightly
  prefix = {
    "pattern": "mem-pattern",
    "anti-pattern": "mem-anti-pattern",
    "preference": "mem-preference",
    "playbook": "mem-playbook",
    "reflection": "mem-reflection",
  }.get(mem_type, "mem")
  return f"{prefix}-{ts}"


def skeleton_body(mem_type: str, title: str) -> str:
  if mem_type == "pattern":
    return f"""# {title}

## 背景与适用场景

## 推荐做法（步骤 / Checklist）

## 反例与常见误区（如有）

## 与现有规范/技能的关系

"""
  if mem_type == "anti-pattern":
    return f"""# {title}

## 反模式描述

## 典型场景

## 推荐替代做法

## 适用环境与注意事项

"""
  if mem_type == "preference":
    return f"""# {title}

> 本条目记录用户或项目的偏好；写入前应获得用户确认，并默认以 draft 形式存在。

## 偏好内容

## 适用范围与例外

"""
  if mem_type == "playbook":
    return f"""# {title}

## 适用场景

## 前置条件

## 执行步骤（SOP）

## 变体与扩展

"""
  if mem_type == "reflection":
    return f"""# {title}

## 背景

## 主要发现与结论

## 对后续迭代的建议

"""
  return f"# {title}\n\n"


def main() -> None:
  parser = argparse.ArgumentParser(
    description="Create a new memory entry under memory/*/ with frontmatter skeleton.",
  )
  parser.add_argument(
    "--type",
    required=True,
    choices=["pattern", "anti-pattern", "preference", "playbook", "reflection"],
    help="Memory type.",
  )
  parser.add_argument(
    "--title",
    required=True,
    help="Title of the memory entry.",
  )
  parser.add_argument(
    "--change-id",
    required=True,
    help="Source change-id that motivates this memory.",
  )
  parser.add_argument(
    "--tags",
    required=True,
    help="Comma-separated tags, e.g. 'openspec,change-flow'.",
  )
  parser.add_argument(
    "--applicable-projects",
    default="ai-agent-dev-system",
    help="Comma-separated applicable projects, default: ai-agent-dev-system. Use 'all' for global.",
  )
  parser.add_argument(
    "--host-scope",
    default="cursor",
    help="Comma-separated host scope, e.g. 'cursor,vscode,continue'. Default: cursor.",
  )
  parser.add_argument(
    "--id",
    default=None,
    help="Optional explicit memory id; if omitted, a timestamp-based id will be generated.",
  )
  parser.add_argument(
    "--maturity",
    default="draft",
    choices=["draft", "experimental", "stable", "deprecated"],
    help="Maturity level, default: draft.",
  )
  parser.add_argument(
    "--owner",
    default=None,
    help="Optional owner (e.g. @billhu).",
  )

  args = parser.parse_args()

  mem_type = args.type
  title = args.title
  change_id = args.change_id
  tags = parse_comma_list(args.tags)
  applicable_projects_raw = parse_comma_list(args.applicable_projects)
  host_scope_raw = parse_comma_list(args.host_scope)

  # Normalize projects/host_scope lists
  applicable_projects = applicable_projects_raw or ["all"]
  host_scope = host_scope_raw or ["generic"]

  now = datetime.now()
  date_str = now.strftime("%Y-%m-%d")

  mem_id = args.id or generate_id(mem_type, title)

  # Decide target subdirectory
  subdir = TYPE_TO_SUBDIR[mem_type]

  root = Path(__file__).resolve().parents[2]
  memory_root = root / "memory"
  target_dir = memory_root / subdir
  target_dir.mkdir(parents=True, exist_ok=True)

  # Derive filename from id (safe, no spaces)
  filename = f"{mem_id}.md"
  target_file = target_dir / filename

  if target_file.exists():
    raise SystemExit(f"Target file already exists: {target_file}")

  # Build frontmatter
  lines = []
  lines.append("---")
  lines.append(f"id: {mem_id}")
  lines.append(f"title: {title}")
  lines.append(f"type: {mem_type}")
  lines.append(f"tags: [{', '.join(tags)}]")
  lines.append(f"applicable_projects: [{', '.join(applicable_projects)}]")
  lines.append(f"host_scope: [{', '.join(host_scope)}]")
  lines.append(f"source_change_ids: [{change_id}]")
  lines.append(f"created_at: {date_str}")
  lines.append(f"last_reviewed_at: {date_str}")
  lines.append(f"maturity: {args.maturity}")
  if args.owner:
    lines.append(f"owner: {args.owner}")
  lines.append("---")
  lines.append("")

  body = skeleton_body(mem_type, title)

  content = "\n".join(lines) + body

  target_file.write_text(content, encoding="utf-8")
  print(f"Created memory entry: {target_file}")


if __name__ == "__main__":
  main()

