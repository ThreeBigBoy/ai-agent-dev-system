"""FastAPI 服务：/run, /status, /health, /resume。"""
from __future__ import annotations

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from .config import get_runtime_logs_root
from .workflow import get_graph, AgentState

logger = logging.getLogger(__name__)
app = FastAPI(title="LangGraph Backend", version="1.0.0")


class RunRequest(BaseModel):
    change_id: str = Field(..., description="变更 ID")
    task_range: str | None = Field(None, description="可选任务范围，如 2.1-2.4（与 phase 互斥）")
    phase: str | None = Field(
        None,
        description="阶段标识，如 env-check/mcp-check/biz-trace/full（与 task_range 互斥，默认 full）",
    )
    workspace_projects: str | None = Field(
        None,
        description='业务项目列表，格式 "key1|path1:key2|path2"；按 change_id 自动解析，无需「当前项目」',
    )
    workspace_root: str | None = Field(
        None,
        description="兼容：业务项目根（单路径或多路径），未设 workspace_projects 时使用",
    )
    project_key: str | None = Field(
        None,
        description="兼容：多路径时仅尝试路径中包含该 key 的根",
    )

    def model_post_init(self, __context: Any) -> None:
        """校验：phase 与 task_range 不能同时指定。"""
        if self.phase is not None and self.task_range is not None:
            raise ValueError("Cannot specify both 'phase' and 'task_range'. Use only one.")


class RunResponse(BaseModel):
    status: str
    change_id: str
    thread_id: str | None = None  # 供 /resume 使用
    phase: str | None = None  # 本次执行的 phase（新增）
    results: list[dict] = []
    feedback: str = ""
    checkpoint_id: str | None = None
    latency_seconds: float = 0.0
    completed_phases: list[str] = []  # 已完成的所有 phases（新增）
    pending_phases: list[str] = []  # 待执行的 phases（新增）
    human_confirm_step: str | None = None  # 若为 waiting_hc2/waiting_hc7 时当前等待的步骤（P1-A5）


class ConfirmPendingResponse(BaseModel):
    request_id: str
    hc_id: str
    change_id: str
    step_name: str
    context_summary: str
    artifacts: list[str] = []


class ConfirmSubmitRequest(BaseModel):
    change_id: str
    request_id: str
    decision: str  # approve | reject | comment
    comment: str | None = None
    reviewer: str = ""


class ResumeRequest(BaseModel):
    change_id: str = Field(...)
    thread_id: str = Field(...)
    checkpoint_id: str = Field(...)


class StatusResponse(BaseModel):
    change_id: str
    status: str
    current_node: str | None = None
    completed_tasks: list[int] = []
    remaining_tasks: list[int] = []


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    executors: list[str] = []


# 内存中记录 thread_id 与 change_id 的对应（单实例 MVP）
_thread_by_change: dict[str, str] = {}


def _append_langgraph_run_log(
    change_id: str,
    thread_id: str,
    status: str,
    task_count: int,
    latency_seconds: float,
    workspace_root: str | None = None,
    project_key: str | None = None,
    checkpoint_id: str | None = None,
    error: str | None = None,
    phase: str | None = None,  # 新增：阶段标识
    total_tasks: int | None = None,  # 新增：全量任务数
    completed_phases: list[str] | None = None,  # 新增：已完成 phases
    pending_phases: list[str] | None = None,  # 新增：待执行 phases
) -> None:
    """新管线留痕：追加一条到 runtime-logs/langgraph-runs/YYYY-MM-DD.jsonl，支持阶段化执行（多阶段留痕）。"""
    root = get_runtime_logs_root()
    if not root:
        return
    runs_dir = root / "langgraph-runs"
    try:
        runs_dir.mkdir(parents=True, exist_ok=True)
    except OSError:
        return
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    payload: dict = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "change_id": change_id,
        "thread_id": thread_id,
        "phase": phase or "full",  # 默认 "full" 保持向后兼容
        "workspace_root": workspace_root,
        "status": status,
        "task_count": task_count,
        "total_tasks": total_tasks,  # 新增
        "latency_seconds": round(latency_seconds, 2),
        "checkpoint_id": checkpoint_id,
        "error": error,
    }
    if project_key is not None:
        payload["project_key"] = project_key
    # 阶段化执行相关字段
    if completed_phases is not None:
        payload["completed_phases"] = completed_phases
    if pending_phases is not None:
        payload["pending_phases"] = pending_phases
    line = json.dumps(payload, ensure_ascii=False) + "\n"
    try:
        (runs_dir / f"{today}.jsonl").open("a", encoding="utf-8").write(line)
    except OSError as e:
        logger.warning("append langgraph run log failed: %s", e)


@app.post("/run", response_model=RunResponse)
def run(req: RunRequest) -> RunResponse:
    """执行工作流，支持阶段化执行（phase 参数）。"""
    start = time.time()
    thread_id = f"{req.change_id}-{uuid.uuid4().hex[:8]}"
    _thread_by_change[req.change_id] = thread_id
    
    # 确定 phase（默认为 "full"）
    phase = req.phase or "full"
    
    initial: AgentState = {
        "change_id": req.change_id,
        "task_range": req.task_range,
        "phase": phase,  # 新增：阶段标识
        "decision": {},
        "results": [],
        "feedback": "",
        "status": "pending",
        "ckpt_ref": None,
        "workspace_root": req.workspace_root,
        "project_key": getattr(req, "project_key", None),
        "workspace_projects": getattr(req, "workspace_projects", None),
        "resolved_workspace_root": None,
        "resolved_project_key": None,
    }
    config: dict[str, Any] = {"configurable": {"thread_id": thread_id}}
    try:
        graph = get_graph()
        final = graph.invoke(initial, config=config)
        if isinstance(final, dict):
            res = final
        else:
            res = dict(final)
        _status_cache[thread_id] = res
        # 取最新检查点 id 供断点续跑
        try:
            snap = graph.get_state(config)
            ckpt_id = (snap.config or {}).get("configurable", {}).get("checkpoint_id") if hasattr(snap, "config") else None
        except Exception:
            ckpt_id = None
        latency = time.time() - start
        
        # 计算 completed_phases 和 pending_phases（简化版，实际应从日志聚合）
        completed_phases = [phase] if res.get("status") == "done" else []
        pending_phases = []  # 当前 phase 执行完成后，无待执行 phases
        
        _append_langgraph_run_log(
            change_id=req.change_id,
            thread_id=thread_id,
            status=res.get("status", "done"),
            task_count=len(res.get("results", [])),
            latency_seconds=latency,
            workspace_root=res.get("resolved_workspace_root") or req.workspace_root,
            project_key=res.get("resolved_project_key") or getattr(req, "project_key", None),
            checkpoint_id=ckpt_id,
            phase=phase,  # 新增
            total_tasks=len(res.get("results", [])),  # 新增
            completed_phases=completed_phases,  # 新增
            pending_phases=pending_phases,  # 新增
        )
        st = res.get("status", "done")
        hc_step = res.get("human_confirm_step")
        if st in ("waiting_hc0", "waiting_hc2", "waiting_hc7") and thread_id and req.change_id:
            step_name = "step0.5_clarification" if st == "waiting_hc0" else ("step4.5_design" if st == "waiting_hc2" else "step7.5_acceptance")
            hc_id = "HC0" if st == "waiting_hc0" else ("HC2" if st == "waiting_hc2" else "HC3")
            # 从 state 带入 artifacts，供前端 ConfirmPanel 展示（Minor 修复）
            if st == "waiting_hc0":
                artifacts = list(res.get("step0_completed") or [])[:20]
            else:
                task_list = res.get("decision") or {}
                artifacts = [str(t.get("task_id", "")) for t in (task_list.get("task_list") or [])][:20]
            _pending_confirm[req.change_id] = {
                "request_id": thread_id,
                "hc_id": hc_id,
                "change_id": req.change_id,
                "step_name": step_name,
                "context_summary": res.get("feedback", "")[:500],
                "artifacts": artifacts,
            }
        return RunResponse(
            status=st,
            change_id=res.get("change_id", req.change_id),
            thread_id=thread_id,
            phase=phase,
            results=res.get("results", []),
            feedback=res.get("feedback", ""),
            checkpoint_id=ckpt_id,
            latency_seconds=round(latency, 2),
            completed_phases=completed_phases,
            pending_phases=pending_phases,
            human_confirm_step=hc_step,
        )
    except FileNotFoundError as e:
        _append_langgraph_run_log(
            change_id=req.change_id, thread_id=thread_id, status="error", task_count=0,
            latency_seconds=time.time() - start, workspace_root=req.workspace_root,
            project_key=getattr(req, "project_key", None), error=str(e), phase=phase,
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        _append_langgraph_run_log(
            change_id=req.change_id, thread_id=thread_id, status="error", task_count=0,
            latency_seconds=time.time() - start, workspace_root=req.workspace_root,
            project_key=getattr(req, "project_key", None), error=str(e), phase=phase,
        )
        raise HTTPException(status_code=500, detail=str(e))


# 内存缓存：thread_id -> 最近一次 state 快照（MVP 用于 /status）
_status_cache: dict[str, dict] = {}

# 人工确认待处理：change_id -> 待确认项（P1-A5，供 /confirm/pending 与 long poll）
_pending_confirm: dict[str, dict] = {}


@app.get("/status/{change_id}", response_model=StatusResponse)
def status(change_id: str) -> StatusResponse:
    """查询某 change-id 的执行状态。"""
    thread_id = _thread_by_change.get(change_id)
    if not thread_id:
        return StatusResponse(change_id=change_id, status="pending")
    vals = _status_cache.get(thread_id)
    if not vals:
        return StatusResponse(change_id=change_id, status="running")
    task_list = (vals.get("decision") or {}).get("task_list", [])
    completed = [r.get("task_id") for r in (vals.get("results") or []) if isinstance(r, dict)]
    remaining = [t["task_id"] for t in task_list if t["task_id"] not in completed]
    return StatusResponse(
        change_id=change_id,
        status=vals.get("status", "running"),
        current_node=None,
        completed_tasks=completed,
        remaining_tasks=remaining,
    )


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """健康检查。"""
    from runtime_config import load_runtime_config
    cfg = load_runtime_config()
    return HealthResponse(executors=cfg.get("executors", []))


@app.post("/resume", response_model=RunResponse)
def resume(req: ResumeRequest) -> RunResponse:
    """从检查点恢复执行：用 thread_id + checkpoint_id 取状态，若未结束则 invoke(None, config) 继续跑。"""
    start = time.time()
    config: dict[str, Any] = {
        "configurable": {
            "thread_id": req.thread_id,
            "checkpoint_id": req.checkpoint_id,
        }
    }
    try:
        graph = get_graph()
        snap = graph.get_state(config)
        next_nodes = getattr(snap, "next", None)
        # 若已结束（无后续节点），直接返回当前状态
        if next_nodes is None or (hasattr(next_nodes, "__len__") and len(next_nodes) == 0):
            vals = getattr(snap, "values", {}) or {}
            if isinstance(vals, dict):
                _status_cache[req.thread_id] = vals
            _thread_by_change[req.change_id] = req.thread_id
            latency = time.time() - start
            _append_langgraph_run_log(
                change_id=req.change_id, thread_id=req.thread_id, status="done",
                task_count=len(vals.get("results", [])), latency_seconds=latency,
                workspace_root=vals.get("resolved_workspace_root") or getattr(req, "workspace_root", None),
                project_key=vals.get("resolved_project_key"), checkpoint_id=req.checkpoint_id,
            )
            return RunResponse(
                status=vals.get("status", "done"),
                change_id=vals.get("change_id", req.change_id),
                thread_id=req.thread_id,
                results=vals.get("results", []),
                feedback=vals.get("feedback", ""),
                checkpoint_id=req.checkpoint_id,
                latency_seconds=round(latency, 2),
            )
        # 未结束：从该检查点继续执行
        final = graph.invoke(None, config=config)
        if isinstance(final, dict):
            res = final
        else:
            res = dict(final)
        _status_cache[req.thread_id] = res
        _thread_by_change[req.change_id] = req.thread_id
        try:
            snap2 = graph.get_state({"configurable": {"thread_id": req.thread_id}})
            ckpt_id = (snap2.config or {}).get("configurable", {}).get("checkpoint_id") if hasattr(snap2, "config") else req.checkpoint_id
        except Exception:
            ckpt_id = req.checkpoint_id
        latency = time.time() - start
        _append_langgraph_run_log(
            change_id=req.change_id, thread_id=req.thread_id, status=res.get("status", "done"),
            task_count=len(res.get("results", [])), latency_seconds=latency,
            workspace_root=res.get("resolved_workspace_root") or getattr(req, "workspace_root", None),
            project_key=res.get("resolved_project_key"), checkpoint_id=ckpt_id,
        )
        return RunResponse(
            status=res.get("status", "done"),
            change_id=res.get("change_id", req.change_id),
            thread_id=req.thread_id,
            results=res.get("results", []),
            feedback=res.get("feedback", ""),
            checkpoint_id=ckpt_id,
            latency_seconds=round(latency, 2),
        )
    except FileNotFoundError as e:
        logger.warning("resume FileNotFoundError: %s", e)
        raise HTTPException(status_code=400, detail=str(e))
    except ValueError as e:
        logger.warning("resume ValueError: %s", e)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("resume unexpected error: %s", e)
        raise HTTPException(status_code=500, detail="服务暂时不可用，请稍后重试或查看服务端日志")


# ---------- 人工确认接口（P1-A5）----------

@app.get("/confirm/pending", response_model=ConfirmPendingResponse)
def confirm_pending(change_id: str):
    """查询当前是否有待人工确认项（waiting_hc2/waiting_hc7 时）。"""
    pending = _pending_confirm.get(change_id)
    if not pending:
        raise HTTPException(status_code=404, detail="无待确认项")
    return ConfirmPendingResponse(**pending)


@app.get("/confirm/poll", response_model=ConfirmPendingResponse | dict)
async def confirm_poll(change_id: str, timeout_seconds: int = 60):
    """Long Poll：在 timeout_seconds 内等待直到出现待确认项或超时。使用 asyncio.sleep 避免阻塞 worker（Minor 修复）。"""
    deadline = time.time() + max(1, min(timeout_seconds, 120))
    while time.time() < deadline:
        pending = _pending_confirm.get(change_id)
        if pending:
            return ConfirmPendingResponse(**pending)
        await asyncio.sleep(1)
    return {"pending": False, "message": "timeout"}


@app.post("/confirm/submit")
def confirm_submit(req: ConfirmSubmitRequest):
    """提交人工确认结果（approve/reject/comment），清除该 change_id 的待确认状态。"""
    if req.decision not in ("approve", "reject", "comment"):
        raise HTTPException(status_code=400, detail="decision 须为 approve | reject | comment")
    _pending_confirm.pop(req.change_id, None)
    return {"ok": True, "change_id": req.change_id, "decision": req.decision}
