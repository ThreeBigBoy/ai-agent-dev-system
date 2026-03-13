#!/usr/bin/env python3
"""
Summarize model call records under runtime-logs/model-calls/*.jsonl.

Usage examples (from repo root):

  # 按日期汇总总调用次数与 status 分布
  python3 scripts/runtime-logging/summarize_model_calls.py --group-by day

  # 按 change-id 汇总
  python3 scripts/runtime-logging/summarize_model_calls.py --group-by change-id

  # 按 host 汇总
  python3 scripts/runtime-logging/summarize_model_calls.py --group-by host

本脚本仅读取本地 JSONL 日志，不访问外部网络，可由主 Agent 在需要时自动或半自动调用。
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple


def iter_records(root: Path) -> Iterable[Dict[str, Any]]:
  model_calls_dir = root / "runtime-logs" / "model-calls"
  if not model_calls_dir.exists():
    return

  for path in sorted(model_calls_dir.glob("*.jsonl")):
    with path.open("r", encoding="utf-8") as f:
      for line in f:
        line = line.strip()
        if not line:
          continue
        try:
          record = json.loads(line)
          if isinstance(record, dict):
            yield record
        except json.JSONDecodeError:
          continue


def extract_day(timestamp: str) -> str:
  try:
    dt = datetime.fromisoformat(timestamp)
    return dt.strftime("%Y-%m-%d")
  except Exception:
    # fallback：直接截取日期部分
    return timestamp.split("T", 1)[0]


def summarize(records: Iterable[Dict[str, Any]], group_by: str) -> Dict[Tuple[str, ...], Counter]:
  summary: Dict[Tuple[str, ...], Counter] = defaultdict(Counter)

  for rec in records:
    change_id = str(rec.get("change_id") or "-")
    host = str(rec.get("host") or "-")
    status = str(rec.get("status") or "-")
    timestamp = str(rec.get("timestamp") or "-")
    day = extract_day(timestamp)

    if group_by == "day":
      key = (day,)
    elif group_by == "change-id":
      key = (change_id,)
    elif group_by == "host":
      key = (host,)
    elif group_by == "day-change-id":
      key = (day, change_id)
    else:
      key = ("all",)

    summary[key]["total"] += 1
    summary[key][f"status={status}"] += 1

  return summary


def print_summary(summary: Dict[Tuple[str, ...], Counter], group_by: str) -> None:
  if not summary:
    print("No model-calls records found under runtime-logs/model-calls/.")
    return

  # Collect all status keys
  status_keys = set()
  for counts in summary.values():
    for k in counts:
      if k.startswith("status="):
        status_keys.add(k)
  status_keys = sorted(status_keys)

  # Header
  if group_by == "day":
    header = ["day", "total"] + status_keys
  elif group_by == "change-id":
    header = ["change_id", "total"] + status_keys
  elif group_by == "host":
    header = ["host", "total"] + status_keys
  elif group_by == "day-change-id":
    header = ["day", "change_id", "total"] + status_keys
  else:
    header = ["scope", "total"] + status_keys

  print("\t".join(header))

  for key, counts in sorted(summary.items()):
    row = list(key)
    row.append(str(counts.get("total", 0)))
    for sk in status_keys:
      row.append(str(counts.get(sk, 0)))
    print("\t".join(row))


def main() -> None:
  parser = argparse.ArgumentParser(
    description="Summarize runtime-logs/model-calls/*.jsonl by day/change-id/host.",
  )
  parser.add_argument(
    "--group-by",
    default="day",
    choices=["day", "change-id", "host", "day-change-id", "all"],
    help="Grouping key for summary (default: day).",
  )

  args = parser.parse_args()

  root = Path(__file__).resolve().parents[2]
  records = iter_records(root)
  summary = summarize(records, args.group_by)
  print_summary(summary, args.group_by)


if __name__ == "__main__":
  main()

