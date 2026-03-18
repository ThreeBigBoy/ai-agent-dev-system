"""
Skill 自动发现 (P4-B1/B2)：扫描 skills 目录下 SKILL.md，返回可用 Skill 列表。
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Any


class SkillAutoDiscovery:
    """扫描 workspace_root/skills 下含 SKILL.md 的子目录。"""

    def __init__(self, workspace_root: Path, skills_dir_name: str = "skills"):
        self.workspace_root = Path(workspace_root)
        self.skills_dir = self.workspace_root / skills_dir_name

    def discover(self) -> List[Dict[str, Any]]:
        """返回 [{"id": str, "path": str, "name": str}, ...]。"""
        result = []
        if not self.skills_dir.is_dir():
            return result
        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue
            skill_id = skill_dir.name
            name = skill_id
            try:
                raw = skill_md.read_text(encoding="utf-8")
                if raw.startswith("---"):
                    end = raw.find("---", 3)
                    if end != -1:
                        block = raw[3:end]
                        m = re.search(r"id:\s*(\S+)", block)
                        if m:
                            skill_id = m.group(1).strip()
                        m = re.search(r"name:\s*(.+)", block)
                        if m:
                            name = m.group(1).strip()
            except Exception:
                pass
            result.append({"id": skill_id, "path": str(skill_md), "name": name})
        return result
