"""
Memory 动态加载 (P4-C1/C2)：扫描 memory 目录，按类型/id 加载条目路径。
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Any


class MemoryLoader:
    """扫描 workspace_root/memory 下 patterns / anti-patterns / reflections 等。"""

    def __init__(self, workspace_root: Path, memory_dir_name: str = "memory"):
        self.workspace_root = Path(workspace_root)
        self.memory_dir = self.workspace_root / memory_dir_name

    def discover(self) -> List[Dict[str, Any]]:
        """返回 [{"id": str, "path": str, "type": str}, ...]。"""
        result = []
        if not self.memory_dir.is_dir():
            return result
        for md in self.memory_dir.rglob("*.md"):
            if md.name.startswith("README") or "schema" in md.name.lower():
                continue
            rel = md.relative_to(self.memory_dir)
            # type: 第一级目录名，如 patterns, anti-patterns
            mem_type = rel.parts[0] if len(rel.parts) > 1 else "misc"
            entry_id = md.stem
            try:
                raw = md.read_text(encoding="utf-8")
                if raw.startswith("---"):
                    end = raw.find("---", 3)
                    if end != -1:
                        m = re.search(r"id:\s*(\S+)", raw[3:end])
                        if m:
                            entry_id = m.group(1).strip()
            except Exception:
                pass
            result.append({"id": entry_id, "path": str(md), "type": mem_type})
        return result

    def load_content(self, entry_id: str) -> str | None:
        """按 id 加载一条 memory 的正文（不含 frontmatter）。"""
        for e in self.discover():
            if e["id"] == entry_id:
                try:
                    text = Path(e["path"]).read_text(encoding="utf-8")
                    if text.startswith("---"):
                        end = text.find("---", 3)
                        if end != -1:
                            text = text[end + 3:].lstrip()
                    return text
                except Exception:
                    return None
        return None
