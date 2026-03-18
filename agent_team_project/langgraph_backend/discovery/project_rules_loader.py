"""
项目规则加载器 (P4-D1/D2)：扫描 project-rules 或 project_rules 目录，返回规则文件路径。
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any


class ProjectRulesLoader:
    """加载业务项目下的 project-rules / project_rules 目录。"""

    def __init__(
        self,
        project_root: Path,
        rules_dir_names: tuple = ("project-rules", "project_rules", ".cursor/rules"),
    ):
        self.project_root = Path(project_root)
        self.rules_dir_names = rules_dir_names

    def discover(self) -> List[Dict[str, Any]]:
        """返回 [{"path": str, "name": str}, ...]。"""
        result = []
        for name in self.rules_dir_names:
            dir_path = self.project_root.joinpath(*name.split("/")) if "/" in name else self.project_root / name
            if not dir_path.is_dir():
                continue
            for f in dir_path.rglob("*"):
                if f.suffix in (".md", ".mdc", ".yaml", ".yml") or f.name.startswith("."):
                    result.append({"path": str(f), "name": f.name})
        return result

    def load_all_content(self) -> str:
        """拼接所有规则文件内容（用于注入 Agent 上下文）。"""
        parts = []
        for item in self.discover():
            try:
                parts.append(Path(item["path"]).read_text(encoding="utf-8"))
            except Exception:
                continue
        return "\n\n---\n\n".join(parts) if parts else ""
