"""LangGraph 状态图：parse_tasks → dispatch → collect_feedback，与 design 2.3 一致。"""
from __future__ import annotations

from typing import List, Optional, TypedDict

from langgraph.constants import END, START
from langgraph.graph import StateGraph
from langgraph.checkpoint.memory import MemorySaver  # alias of InMemorySaver

from .parser import parse_tasks_md
from . import executors as ex


class AgentState(TypedDict):
    change_id: str
    task_range: Optional[str]
    decision: dict
    results: List[dict]
    feedback: str
    status: str
    ckpt_ref: Optional[str]  # 检查点 ID 引用（避免与 LangGraph 保留名 checkpoint_id 冲突）
    workspace_root: Optional[str]  # 兼容：业务项目根（单路径或多路径）
    project_key: Optional[str]  # 兼容：多路径时过滤用
    workspace_projects: Optional[str]  # 推荐：业务项目列表 "key1|path1:key2|path2"，按 change_id 自动解析
    resolved_workspace_root: Optional[str]  # 解析得到的项目根（留痕用）
    resolved_project_key: Optional[str]  # 解析得到的项目 key（留痕用）


def parse_tasks(state: AgentState) -> dict:
    """节点：从 tasks.md 解析任务，写入 decision；若使用 workspace_projects 则写入 resolved_* 供留痕。"""
    change_id = state["change_id"]
    task_range = state.get("task_range")
    workspace_projects = state.get("workspace_projects") or None
    workspace_root = state.get("workspace_root") or None
    project_key = state.get("project_key") or None
    decision = parse_tasks_md(
        change_id, task_range,
        project_root=workspace_root,
        project_key=project_key,
        workspace_projects=workspace_projects,
    )
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
    """构建并编译 StateGraph，可选检查点。"""
    builder = StateGraph(AgentState)
    builder.add_node("parse_tasks", parse_tasks)
    builder.add_node("dispatch", dispatch)
    builder.add_node("collect_feedback", collect_feedback)
    builder.add_edge(START, "parse_tasks")
    builder.add_edge("parse_tasks", "dispatch")
    builder.add_edge("dispatch", "collect_feedback")
    builder.add_edge("collect_feedback", END)
    checkpointer = MemorySaver() if use_checkpointer else None
    return builder.compile(checkpointer=checkpointer)


# 单例图，供 server 使用
_graph = None


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph(use_checkpointer=True)
    return _graph
