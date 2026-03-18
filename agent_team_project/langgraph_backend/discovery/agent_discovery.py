"""
Agent 自动发现 (P4-A1/A2)：扫描 agents 目录，返回可用 Agent 列表。
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List, Any


class AgentAutoDiscovery:
    """扫描 workspace_root/agents 下 .md 文件，解析 frontmatter 或文件名作为 id。"""

    def __init__(self, workspace_root: Path, agents_dir_name: str = "agents"):
        self.workspace_root = Path(workspace_root)
        self.agents_dir = self.workspace_root / agents_dir_name

    def discover(self) -> List[Dict[str, Any]]:
        """返回 [{"id": str, "path": str, "name": str}, ...]。"""
        result = []
        if not self.agents_dir.is_dir():
            return result
        for path in self.agents_dir.glob("**/*.md"):
            if path.name.startswith("README"):
                continue
            rel = path.relative_to(self.agents_dir)
            # id: 文件名去掉 .md，如 子Agent-前端 -> 子Agent-前端
            agent_id = path.stem
            name = agent_id
            # 简单 frontmatter 解析（可选）
            try:
                raw = path.read_text(encoding="utf-8")
                if raw.startswith("---"):
                    end = raw.find("---", 3)
                    if end != -1:
                        block = raw[3:end]
                        m = re.search(r"id:\s*(\S+)", block)
                        if m:
                            agent_id = m.group(1).strip()
                        m = re.search(r"name:\s*(.+)", block)
                        if m:
                            name = m.group(1).strip()
            except Exception:
                pass
            result.append({"id": agent_id, "path": str(path), "name": name})
        return result
