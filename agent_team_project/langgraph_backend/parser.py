"""从 openspec/changes/{change_id}/tasks.md 解析任务列表，生成标准化决策对象。"""
from __future__ import annotations

import re
from pathlib import Path

from .config import get_openspec_changes_dir, get_openspec_changes_dir_for

# 章节负责人到 runtime 7 个 executor 的映射
AGENT_TO_EXECUTOR = {
    "架构 Agent": "架构师",
    "产品经理 Agent": "产品经理",
    "前端 Agent": "前端工程师",
    "后端 Agent": "后端工程师",
    "测试 Agent": "测试工程师",
    "文档 Agent": "文档 Agent",
    "Bug 修复 Agent": "Bug 修复 Agent",
    "主 Agent": "主 Agent",
}

# 多路径分隔符：支持 "PATH1:PATH2" 或 "PATH1;PATH2"（Windows）
_WORKSPACE_ROOT_SEP = (":", ";")
# 业务项目列表格式：key|path，项目间用 : 或 ; 分隔
_WORKSPACE_PROJECTS_PAIR_SEP = (":", ";")
_WORKSPACE_PROJECTS_KEY_PATH_SEP = "|"


def _parse_workspace_projects(raw: str) -> list[tuple[str, Path]]:
    """
    解析 workspace_projects 字符串为 [(project_key, root_path), ...]。
    格式：key1|path1:key2|path2（项目间 : 或 ; 分隔，单项为 key|path）。
    用于「按 change_id 自动解析项目」：后端按顺序尝试每个 path，第一个存在该 change 的即命中。
    """
    raw = (raw or "").strip()
    if not raw:
        return []
    for sep in _WORKSPACE_PROJECTS_PAIR_SEP:
        if sep in raw:
            parts = [p.strip() for p in raw.split(sep) if p.strip()]
            break
    else:
        parts = [raw]
    result: list[tuple[str, Path]] = []
    for p in parts:
        if _WORKSPACE_PROJECTS_KEY_PATH_SEP in p:
            key, _, path = p.partition(_WORKSPACE_PROJECTS_KEY_PATH_SEP)
            key, path = key.strip(), path.strip()
            if key and path:
                result.append((key, Path(path)))
    return result


def _normalize_workspace_roots(
    workspace_root: str | Path | None,
    project_key: str | None = None,
) -> list[Path]:
    """
    将 workspace_root 规范为 Path 列表，便于多业务项目匹配。
    - workspace_root 可为单路径或多路径字符串（用 : 或 ; 分隔）。
    - project_key 可选：若提供，仅保留路径字符串中包含 project_key 的根（关键路径/项目名匹配）。
    """
    if workspace_root is None:
        return []
    raw = str(workspace_root).strip()
    if not raw:
        return []
    # 先按分隔符拆成多个路径
    for sep in _WORKSPACE_ROOT_SEP:
        if sep in raw:
            parts = [p.strip() for p in raw.split(sep) if p.strip()]
            break
    else:
        parts = [raw]
    roots = [Path(p) for p in parts if p]
    if project_key and project_key.strip():
        key = project_key.strip()
        roots = [r for r in roots if key in str(r)]
    return roots


def parse_tasks_md(
    change_id: str,
    task_range: str | None = None,
    project_root: str | Path | None = None,
    project_key: str | None = None,
    workspace_projects: str | None = None,
) -> dict:
    """
    解析 openspec/changes/{change_id}/tasks.md，返回标准化决策对象。
    - workspace_projects（推荐）：业务项目列表，格式 "key1|path1:key2|path2"。按 change_id 自动解析：
      先本仓，再按列表顺序尝试每个 path，第一个存在该 change_id 的 tasks.md 即命中，无需「当前项目」配置。
      命中后会在返回 dict 中写入 resolved_workspace_root、resolved_project_key 供留痕。
    - project_root / project_key（兼容）：未提供 workspace_projects 时使用；多路径时可按 project_key 过滤。
    - task_range 可选，支持 "2.1-2.4" 或 "2.1"。
    """
    resolved_workspace_root: str | None = None
    resolved_project_key: str | None = None

    # 1. 优先尝试本仓（ai-agent-dev-system）的 openspec/changes
    primary_dir = get_openspec_changes_dir()
    primary_path: Path | None = None
    if primary_dir is not None:
        candidate = primary_dir / change_id / "tasks.md"
        if candidate.is_file():
            primary_path = candidate

    # 2. 再尝试业务项目
    secondary_path: Path | None = None
    tried_roots: list[Path] = []
    roots: list[Path] = []
    use_projects_list = (workspace_projects or "").strip()

    if use_projects_list:
        # 新范式：workspace_projects 列表，按 change_id 自动解析（顺序尝试，第一个存在即命中）
        pairs = _parse_workspace_projects(workspace_projects)
        for k, root in pairs:
            proj_dir = get_openspec_changes_dir_for(root)
            if proj_dir is not None:
                candidate = proj_dir / change_id / "tasks.md"
                tried_roots.append(root)
                if candidate.is_file():
                    secondary_path = candidate
                    resolved_workspace_root = str(root)
                    resolved_project_key = k
                    break
    else:
        roots = _normalize_workspace_roots(project_root, project_key)
        for root in roots:
            proj_dir = get_openspec_changes_dir_for(root)
            if proj_dir is not None:
                candidate = proj_dir / change_id / "tasks.md"
                tried_roots.append(root)
                if candidate.is_file():
                    secondary_path = candidate
                    break

    # 3. 选择路径：本仓优先，找不到再用业务项目
    if primary_path is not None:
        path = primary_path
    elif secondary_path is not None:
        path = secondary_path
    else:
        err_extra = f"本仓路径={primary_dir}, change_id={change_id}"
        if tried_roots:
            err_extra += f", 已尝试业务根={tried_roots}"
        if use_projects_list:
            err_extra += ", workspace_projects 中无项目包含该 change_id"
        elif project_key:
            err_extra += f", project_key={project_key!r}"
        else:
            err_extra += ", 未提供或经 project_key 过滤后无业务根"
        raise FileNotFoundError(f"tasks.md 不存在于本仓或传入的 workspace_root；{err_extra}")

    text = path.read_text(encoding="utf-8")
    lines = text.split("\n")
    task_list: list[dict] = []
    current_section_executor = "产品经理"
    range_start, range_end = None, None
    if task_range:
        s = task_range.strip()
        r = re.match(r"^(\d+)\.(\d+)-(\d+)\.(\d+)$", s)
        if r:
            range_start = (int(r.group(1)), int(r.group(2)))
            range_end = (int(r.group(3)), int(r.group(4)))
        else:
            single = re.match(r"^(\d+)\.(\d+)$", s)
            if single:
                a, b = int(single.group(1)), int(single.group(2))
                range_start = range_end = (a, b)
    i = 0
    while i < len(lines):
        line = lines[i]
        # 章节：## 2. 后端实现（后端 Agent）
        section_m = re.match(r"^##\s+\d+\.\s+.+?[（(]([^）)]+)[）)]", line)
        if section_m:
            current_section_executor = section_m.group(1).strip()
            i += 1
            continue
        # 任务行：- [ ] 2.1 创建 `langgraph_backend/` 目录结构
        task_m = re.match(r"^\s*-\s*\[\s*[xX ]?\s*]\s+(\d+)\.(\d+)\s+(.+)$", line)
        if task_m:
            sec, sub = int(task_m.group(1)), int(task_m.group(2))
            task_name = task_m.group(3).strip()
            if range_start and range_end:
                if (sec, sub) < range_start or (sec, sub) > range_end:
                    i += 1
                    continue
            executor = AGENT_TO_EXECUTOR.get(current_section_executor, current_section_executor)
            input_req = task_name
            j = i + 1
            while j < len(lines) and (lines[j].startswith("  **") or lines[j].strip() == ""):
                next_line = lines[j]
                if "**负责人**" in next_line:
                    ex_m = re.search(r"\*\*负责人\*\*:\s*([^\n*]+)", next_line)
                    if ex_m:
                        executor = AGENT_TO_EXECUTOR.get(ex_m.group(1).strip(), ex_m.group(1).strip())
                if "**输入**" in next_line:
                    in_m = re.search(r"\*\*输入\*\*:\s*(.+)", next_line)
                    if in_m:
                        input_req = in_m.group(1).strip()
                if "**输出**" in next_line and not input_req:
                    out_m = re.search(r"\*\*输出\*\*:\s*(.+)", next_line)
                    if out_m:
                        input_req = "输出: " + out_m.group(1).strip()
                j += 1
            task_id = sec * 100 + sub
            task_list.append({
                "task_id": task_id,
                "task_name": task_name,
                "executor": executor,
                "input_requirement": input_req,
                "dependency": 0,
            })
            i = j
            continue
        i += 1
    task_list.sort(key=lambda x: x["task_id"])
    # 重排 task_id 为 1,2,3... 以便与 design 示例一致（可选，保留原 101,102 也可）
    for idx, t in enumerate(task_list, 1):
        t["task_id"] = idx
    out: dict = {
        "change_id": change_id,
        "task_complexity": "复杂",
        "matched_scene": "scene1-openspec-fullflow",
        "reason": f"从 tasks.md 解析 change_id={change_id}",
        "task_list": task_list,
    }
    if resolved_workspace_root is not None:
        out["resolved_workspace_root"] = resolved_workspace_root
    if resolved_project_key is not None:
        out["resolved_project_key"] = resolved_project_key
    return out
