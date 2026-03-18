"""LangGraph 状态图：step0_clarification → hc0_gate → parse_tasks → hc2_gate → dispatch → collect_feedback → hc7_gate。
支持阶段化执行（phase 参数）。
V2.11.0：Step 1-4 产出物前置检查。
V2.11.1 P1-A1：Step 4.5/7.5 人工确认门控（hc2_gate/hc7_gate）。
V2.11.1 P2-A6：Step 0 需求澄清层 + HC0 门控（step0_clarification / hc0_gate）。
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Optional, TypedDict

from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver  # alias of InMemorySaver

from .parser import parse_tasks_md
from . import executors as ex
from .config import DEFAULT_PHASES, PACKAGE_DIR


class AgentState(TypedDict):
    change_id: str
    task_range: Optional[str]
    phase: Optional[str]  # 阶段标识（env-check/mcp-check/biz-trace/full）
    decision: dict
    results: List[dict]
    feedback: str
    status: str
    ckpt_ref: Optional[str]
    workspace_root: Optional[str]
    project_key: Optional[str]
    workspace_projects: Optional[str]
    resolved_workspace_root: Optional[str]
    resolved_project_key: Optional[str]
    human_confirmed: Optional[bool]
    human_confirm_step: Optional[str]
    # P2-A6/A7：Step 0 需求澄清
    step0_output: Optional[dict]  # 各子步骤产出 { "0.1": {...}, ... }
    step0_skip: Optional[List[str]]  # 要跳过的子步骤 ID，如 ["0.2", "0.7"]
    step0_retry: Optional[List[str]]  # 要重做的子步骤 ID
    step0_completed: Optional[List[str]]  # 已完成的子步骤 ID 列表


def _check_prerequisites(change_id: str, workspace_root: Path) -> dict:
    """
    检查 Step 1-4 产出物是否存在（前置条件检查）。
    返回检查结果，如有缺失则返回详细提示。
    V2.11.0 新增：6.2 短期行动 - Step 1-4 产出物检查
    """
    results = {
        "all_passed": True,
        "missing": []
    }
    
    change_dir = workspace_root / "design" / "documents" / "changes" / change_id
    records_dir = change_dir / "records"
    
    # Step 1: PRD 存在性检查
    prd_files = list(change_dir.glob(f"PRD-{change_id}*.md"))
    if not prd_files:
        results["all_passed"] = False
        results["missing"].append({
            "step": 1,
            "name": "PRD",
            "path": f"design/documents/changes/{change_id}/PRD-{change_id}-[关键词].md",
            "action": "请先执行 request-analysis 产出 PRD"
        })
    
    # Step 2: PRD 评审纪要存在性检查
    prd_review_file = records_dir / f"PRD-{change_id}-评审纪要.md"
    if not prd_review_file.exists():
        results["all_passed"] = False
        results["missing"].append({
            "step": 2,
            "name": "PRD 评审纪要",
            "path": f"design/documents/changes/{change_id}/records/PRD-{change_id}-评审纪要.md",
            "action": "请先执行 prd-review 评审 PRD"
        })
    
    # Step 3: 技术方案存在性检查（支持 design/documents 与 openspec/changes 两处）
    design_files = list(change_dir.glob(f"技术方案-{change_id}*.md"))
    openspec_design = workspace_root / "openspec" / "changes" / change_id / "design.md"
    if not design_files and not openspec_design.exists():
        results["all_passed"] = False
        results["missing"].append({
            "step": 3,
            "name": "技术方案",
            "path": f"design/documents/changes/{change_id}/技术方案-*.md 或 openspec/changes/{change_id}/design.md",
            "action": "请先执行 project-analysis 产出技术方案"
        })
    
    # Step 4: 技术方案评审纪要存在性检查（兼容 技术方案-* 与 design-* 命名）
    design_review_file = records_dir / f"技术方案-{change_id}-评审纪要.md"
    design_review_alt = records_dir / f"design-{change_id}-评审纪要.md"
    if not design_review_file.exists() and not design_review_alt.exists():
        results["all_passed"] = False
        results["missing"].append({
            "step": 4,
            "name": "技术方案评审纪要",
            "path": f"design/documents/changes/{change_id}/records/技术方案-{change_id}-评审纪要.md",
            "action": "请先执行 architecture-review 评审技术方案"
        })
    
    return results


def _get_workspace_root_for_checks(state: AgentState) -> Path:
    """解析 workflow 用于前置/HC 检查的工作区根。"""
    ws = state.get("workspace_root") or state.get("resolved_workspace_root")
    if ws and Path(ws).is_dir():
        return Path(ws)
    from .config import get_openspec_changes_dir
    default_dir = get_openspec_changes_dir()
    if default_dir and default_dir.parent.parent.is_dir():
        return default_dir.parent.parent
    return Path.cwd()


# ---------- Step 0 需求澄清（P2-A6 / P2-A7）----------

STEP0_PROMPTS_DIR = PACKAGE_DIR / "step0_prompts"
STEP0_SUBSTEP_IDS = ["0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "0.9", "0.10"]
STEP0_FILE_MAP = {
    "0.1": "01_intent.md",
    "0.2": "02_context.md",
    "0.3": "03_stakeholders.md",
    "0.4": "04_scope.md",
    "0.5": "05_success_criteria.md",
    "0.6": "06_constraints.md",
    "0.7": "07_glossary.md",
    "0.8": "08_assumptions_risks.md",
    "0.9": "09_acceptance_draft.md",
    "0.10": "10_summary.md",
}


def _run_step0_substep(substep_id: str, prompt_path: Path) -> dict:
    """执行单个 Step 0 子步骤：读取 prompt 并产出占位结果。后续可在此处接入 LLM 或独立执行器（Minor 文档化）。"""
    try:
        raw = prompt_path.read_text(encoding="utf-8")
        return {"status": "completed", "prompt_preview": raw[:500], "output": "(执行结果占位，可接 LLM)"}
    except Exception as e:
        return {"status": "error", "error": str(e), "output": ""}


def step0_clarification(state: AgentState) -> dict:
    """
    Step 0 需求澄清：按 10 个子步骤顺序执行或跳过/重做，产出 step0_output 与 step0_completed。
    P2-A6 / P2-A7：支持 step0_skip 与 step0_retry。
    """
    skip_list = list(state.get("step0_skip") or [])
    retry_list = list(state.get("step0_retry") or [])
    prev_output = dict(state.get("step0_output") or {})
    completed = list(state.get("step0_completed") or [])

    out = dict(prev_output)
    for substep_id in STEP0_SUBSTEP_IDS:
        do_skip = substep_id in skip_list and substep_id not in retry_list
        if do_skip:
            out[substep_id] = {"status": "skipped", "output": "已跳过"}
            if substep_id not in completed:
                completed.append(substep_id)
            continue
        fname = STEP0_FILE_MAP.get(substep_id)
        if not fname:
            continue
        prompt_path = STEP0_PROMPTS_DIR / fname
        if not prompt_path.exists():
            out[substep_id] = {"status": "error", "error": f"prompt not found: {fname}", "output": ""}
            completed.append(substep_id)
            continue
        result = _run_step0_substep(substep_id, prompt_path)
        out[substep_id] = result
        if substep_id not in completed:
            completed.append(substep_id)

    return {
        "step0_output": out,
        "step0_completed": completed,
        "status": "running",
        "feedback": f"Step 0 需求澄清已完成，共 {len(completed)} 个子步骤。",
    }


def _hc0_gate(state: AgentState) -> dict:
    """
    HC0 门控：Step 0 与 Step 1 之间的人工确认。
    若 records 下存在 {change_id}-step0.5-clarification-confirmation.md 则放行，否则返回 waiting_hc0。
    P2-A6
    """
    change_id = state["change_id"]
    root = _get_workspace_root_for_checks(state)
    records_dir = root / "design" / "documents" / "changes" / change_id / "records"
    confirmation_file = records_dir / f"{change_id}-step0.5-clarification-confirmation.md"
    if confirmation_file.exists():
        return {"status": "running", "human_confirm_step": None}
    return {
        "status": "waiting_hc0",
        "human_confirm_step": "step0.5_clarification",
        "feedback": "等待需求澄清人工确认（Step 0.5）。请完成确认并落盘 records 下 step0.5-clarification-confirmation 后重新执行。",
    }


def _route_after_hc0(state: AgentState) -> str:
    """HC0 门控后路由：若 waiting_hc0 则结束，否则进入 parse_tasks。"""
    if state.get("status") == "waiting_hc0":
        return "end"
    return "parse_tasks"


def _hc2_gate(state: AgentState) -> dict:
    """
    Step 4.5 门控：技术方案人工确认。
    若 records 下存在 {change_id}-step4.5-design-confirmation.md 则放行，否则返回 waiting_hc2。
    P1-A1 新增
    """
    change_id = state["change_id"]
    root = _get_workspace_root_for_checks(state)
    records_dir = root / "design" / "documents" / "changes" / change_id / "records"
    confirmation_file = records_dir / f"{change_id}-step4.5-design-confirmation.md"
    if confirmation_file.exists():
        return {"status": "running", "human_confirm_step": None}
    return {
        "status": "waiting_hc2",
        "human_confirm_step": "step4.5_design",
        "feedback": "等待技术方案人工确认（Step 4.5）。请完成确认并落盘 records 下 step4.5-design-confirmation 后重新执行。",
    }


def _hc7_gate(state: AgentState) -> dict:
    """
    Step 7.5 门控：功能验收人工确认。
    若 records 下存在 {change_id}-step7.5-acceptance-confirmation.md 则放行，否则返回 waiting_hc7。
    P1-A1 新增
    """
    change_id = state["change_id"]
    root = _get_workspace_root_for_checks(state)
    records_dir = root / "design" / "documents" / "changes" / change_id / "records"
    confirmation_file = records_dir / f"{change_id}-step7.5-acceptance-confirmation.md"
    if confirmation_file.exists():
        return {"status": "done", "human_confirm_step": None}
    return {
        "status": "waiting_hc7",
        "human_confirm_step": "step7.5_acceptance",
        "feedback": "等待功能验收人工确认（Step 7.5）。请完成确认并落盘 step7.5-acceptance-confirmation 后重新执行。",
    }


def _route_after_parse_tasks(state: AgentState) -> str:
    """parse_tasks 后路由：若前置未通过则结束，否则进入 hc2_gate。"""
    if state.get("status") == "blocked":
        return "end"
    return "hc2_gate"


def _route_after_hc2(state: AgentState) -> str:
    """HC2 门控后路由：若 waiting_hc2 则结束，否则进入 dispatch。"""
    if state.get("status") == "waiting_hc2":
        return "end"
    return "dispatch"


def _format_missing_message(missing: list[dict]) -> str:
    """格式化缺失产出物的提示信息。"""
    lines = [
        "**前置阶段产出物检查未通过**",
        "",
        "以下前期阶段产出物缺失，请先完成后再执行：",
        ""
    ]
    for item in missing:
        lines.append(f"**Step {item['step']}: {item['name']}**")
        lines.append(f"- 期望路径: `{item['path']}`")
        lines.append(f"- 建议操作: {item['action']}")
        lines.append("")
    lines.append("**注意**: 根据 10步质量闭环流程，必须先完成需求分析 → PRD评审 → 工程分析 → 方案评审，才能进入编码实现阶段。")
    return "\n".join(lines)


def _get_tasks_for_phase(task_list: list[dict], phase: str | None) -> list[dict]:
    """根据 phase 过滤任务列表。"""
    if phase is None or phase == "full":
        return task_list
    
    phase_config = DEFAULT_PHASES.get(phase)
    if phase_config is None:
        return task_list  # 未知 phase，返回全部任务
    
    task_patterns = phase_config.get("task_patterns", "all")
    if task_patterns == "all":
        return task_list
    
    # 按 task_id 匹配
    filtered = []
    for task in task_list:
        task_id = task.get("task_id", "")
        # 直接匹配或模式匹配（如 "1.*" 匹配 "1.1", "1.2" 等）
        for pattern in task_patterns:
            if task_id == pattern:
                filtered.append(task)
                break
            # 支持通配符匹配（如 "1.*"）
            if pattern.endswith(".*"):
                prefix = pattern[:-2]  # 去掉 "*"
                if task_id.startswith(prefix + "."):
                    filtered.append(task)
                    break
    return filtered


def parse_tasks(state: AgentState) -> dict:
    """节点：从 tasks.md 解析任务，根据 phase 过滤，写入 decision；若使用 workspace_projects 则写入 resolved_* 供留痕。
    V2.11.0 新增：前置 Step 1-4 产出物检查
    """
    change_id = state["change_id"]
    task_range = state.get("task_range")
    phase = state.get("phase")  # 新增：阶段标识
    workspace_projects = state.get("workspace_projects") or None
    workspace_root = state.get("workspace_root") or None
    project_key = state.get("project_key") or None
    
    # V2.11.0 新增：Step 1-4 产出物前置检查
    # 确定检查路径：优先使用传入的 workspace_root，否则使用本仓
    check_root = _get_workspace_root_for_checks({
        "workspace_root": workspace_root,
        "resolved_workspace_root": None,
    })
    check_result = _check_prerequisites(change_id, check_root)
    if not check_result["all_passed"]:
        # 阻断执行，返回详细提示
        return {
            "decision": {
                "error": "prerequisites_not_met",
                "missing": check_result["missing"],
                "task_list": [],  # 空任务列表
            },
            "status": "blocked",
            "feedback": _format_missing_message(check_result["missing"]),
        }
    
    # 继续原有解析逻辑
    decision = parse_tasks_md(
        change_id, task_range,
        project_root=workspace_root,
        project_key=project_key,
        workspace_projects=workspace_projects,
    )
    
    # 根据 phase 过滤任务（阶段化执行支持）
    task_list = decision.get("task_list", [])
    filtered_tasks = _get_tasks_for_phase(task_list, phase)
    decision["task_list"] = filtered_tasks
    decision["phase"] = phase or "full"  # 记录当前 phase
    decision["total_tasks"] = len(task_list)  # 记录全量任务数
    decision["filtered_task_count"] = len(filtered_tasks)  # 记录过滤后的任务数
    
    out: dict = {"decision": decision, "status": "running"}
    if decision.get("resolved_workspace_root") is not None:
        out["resolved_workspace_root"] = decision["resolved_workspace_root"]
    if decision.get("resolved_project_key") is not None:
        out["resolved_project_key"] = decision["resolved_project_key"]
    return out


def dispatch(state: AgentState) -> dict:
    """节点：按 task_list 调用 7 个 executor，结果写入 results。"""
    decision = state["decision"]
    task_list = decision.get("task_list", [])
    results = list(state.get("results") or [])
    for task in sorted(task_list, key=lambda x: x["task_id"]):
        one = ex.run_one_task(
            task["executor"],
            task["task_id"],
            task["task_name"],
            task.get("input_requirement", task["task_name"]),
        )
        results.append(one)
    return {"results": results, "status": "running"}


def collect_feedback(state: AgentState) -> dict:
    """节点：汇总 results 为 feedback 字符串。使用 .get() 兼容 executor 返回格式扩展。"""
    results = state.get("results") or []
    lines = [
        f"任务 {r.get('task_id', '')}（{r.get('executor', '')}）：{r.get('status', '')} - {(r.get('feedback') or r.get('output') or '')[:200]}"
        for r in results
    ]
    feedback = "\n".join(lines)
    return {"feedback": feedback, "status": "done"}


def build_graph(use_checkpointer: bool = True):
    """
    构建并编译 StateGraph。
    流程：step0_clarification → hc0_gate → [parse_tasks | END]；parse_tasks → hc2_gate → ... → hc7_gate → END。
    V2.11.1 P2-A6：Step 0 + HC0；P1-A1：HC2/HC7。
    """
    builder = StateGraph(AgentState)
    builder.add_node("step0_clarification", step0_clarification)
    builder.add_node("hc0_gate", _hc0_gate)
    builder.add_node("parse_tasks", parse_tasks)
    builder.add_node("hc2_gate", _hc2_gate)
    builder.add_node("dispatch", dispatch)
    builder.add_node("collect_feedback", collect_feedback)
    builder.add_node("hc7_gate", _hc7_gate)
    builder.add_edge(START, "step0_clarification")
    builder.add_edge("step0_clarification", "hc0_gate")
    builder.add_conditional_edges("hc0_gate", _route_after_hc0, {"parse_tasks": "parse_tasks", "end": END})
    builder.add_conditional_edges("parse_tasks", _route_after_parse_tasks, {"hc2_gate": "hc2_gate", "end": END})
    builder.add_conditional_edges("hc2_gate", _route_after_hc2, {"dispatch": "dispatch", "end": END})
    builder.add_edge("dispatch", "collect_feedback")
    builder.add_edge("collect_feedback", "hc7_gate")
    builder.add_edge("hc7_gate", END)
    checkpointer = MemorySaver() if use_checkpointer else None
    return builder.compile(checkpointer=checkpointer)


# 单例图，供 server 使用
_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph(use_checkpointer=True)
    return _graph
