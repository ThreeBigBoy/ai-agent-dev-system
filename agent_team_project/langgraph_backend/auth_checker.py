"""
权限检查器 (P3-A2)：变更级权限控制，角色矩阵。
与 design.md 第 11 章一致。
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional


class AuthChecker:
    """变更级权限：read / write / confirm / approve / delete。"""

    ROLE_PERMISSIONS: Dict[str, list] = {
        "owner": ["read", "write", "confirm", "approve", "delete"],
        "maintainer": ["read", "write", "confirm", "approve"],
        "developer": ["read", "write", "confirm"],
        "viewer": ["read"],
    }

    def __init__(self, workspace_root: Path):
        self.workspace_root = Path(workspace_root)
        self._cache: Dict[str, dict] = {}

    def has_permission(
        self,
        change_id: str,
        user_identity: str,
        required_action: str,
    ) -> bool:
        if ":" in user_identity:
            role, _ = user_identity.split(":", 1)
        else:
            role = self._infer_role(change_id, user_identity)
        allowed = self.ROLE_PERMISSIONS.get(role, [])
        return required_action in allowed

    def _infer_role(self, change_id: str, username: str) -> str:
        roles_file = self.workspace_root / ".cursor" / "user-roles.yaml"
        if roles_file.exists():
            try:
                import yaml
                with open(roles_file, "r", encoding="utf-8") as f:
                    cfg = yaml.safe_load(f) or {}
                return cfg.get(username, {}).get("role", "viewer")
            except Exception:
                pass
        return "developer"
