"""
审计日志器 (P3-A3)：关键操作不可篡改记录。
与 design.md 第 11 章一致。
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


class AuditLogger:
    """记录人工确认、Agent 调用等，JSONL 追加写入。"""

    def __init__(self, workspace_root: Path):
        self.workspace_root = Path(workspace_root)
        self.audit_dir = self.workspace_root / ".audit"
        self.audit_dir.mkdir(parents=True, exist_ok=True)

    def log_confirmation(
        self,
        state: Dict[str, Any],
        validated_input: Dict[str, Any],
        signature: str = "",
    ) -> Dict[str, Any]:
        change_id = state.get("change_id", "unknown")
        step = state.get("current_step", "unknown")
        raw = str(validated_input.get("sanitized", ""))
        input_hash = hashlib.sha256(raw.encode()).hexdigest()[:16]
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "change_id": change_id,
            "step": step,
            "action": "human_confirmation",
            "user_identity": state.get("user_identity", "unknown"),
            "input_hash": input_hash,
            "signature": signature,
            "validation_status": "passed" if validated_input.get("valid") else "failed",
            "warnings": validated_input.get("warnings", []),
        }
        path = self.audit_dir / f"{change_id}-{step}-{datetime.utcnow().strftime('%Y%m%d')}.jsonl"
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        return log_entry

    def log_agent_invocation(
        self,
        change_id: str,
        agent_role: str,
        skill: str,
        result: Dict[str, Any],
    ) -> Dict[str, Any]:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "change_id": change_id,
            "action": "agent_invocation",
            "agent_role": agent_role,
            "skill": skill,
            "success": result.get("success"),
            "execution_time_ms": result.get("execution_time_ms"),
            "retry_count": result.get("retry_count", 0),
        }
        path = self.audit_dir / f"{change_id}-agent-{datetime.utcnow().strftime('%Y%m%d')}.jsonl"
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        return log_entry
