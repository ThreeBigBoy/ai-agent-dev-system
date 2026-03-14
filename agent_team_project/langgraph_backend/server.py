"""FastAPI 服务：/run, /status, /health, /resume。"""
from __future__ import annotations

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
    task_range: str | None = Field(None, description="可选任务范围，如 2.1-2.4")
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


class RunResponse(BaseModel):
    status: str
    change_id: str
    thread_id: str | None = None  # 供 /resume 使用
    results: list[dict] = []
    feedback: str = ""
    checkpoint_id: str | None = None
    latency_seconds: float = 0.0


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
) -> None:
    """新管线留痕：追加一条到 runtime-logs/langgraph-runs/YYYY-MM-DD.jsonl，不依赖迭代日志或 design/documents。"""
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
        "workspace_root": workspace_root,
        "status": status,
        "task_count": task_count,
        "latency_seconds": round(latency_seconds, 2),
        "checkpoint_id": checkpoint_id,
        "error": error,
    }
    if project_key is not None:
        payload["project_key"] = project_key
    line = json.dumps(payload, ensure_ascii=False) + "\n"
    try:
        (runs_dir / f"{today}.jsonl").open("a", encoding="utf-8").write(line)
    except OSError as e:
        logger.warning("append langgraph run log failed: %s", e)


@app.post("/run", response_model=RunResponse)
def run(req: RunRequest) -> RunResponse:
    """执行完整工作流。"""
    start = time.time()
    thread_id = f"{req.change_id}-{uuid.uuid4().hex[:8]}"
    _thread_by_change[req.change_id] = thread_id
    initial: AgentState = {
        "change_id": req.change_id,
        "task_range": req.task_range,
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
        _append_langgraph_run_log(
            change_id=req.change_id,
            thread_id=thread_id,
            status=res.get("status", "done"),
            task_count=len(res.get("results", [])),
            latency_seconds=latency,
            workspace_root=res.get("resolved_workspace_root") or req.workspace_root,
            project_key=res.get("resolved_project_key") or getattr(req, "project_key", None),
            checkpoint_id=ckpt_id,
        )
        return RunResponse(
            status=res.get("status", "done"),
            change_id=res.get("change_id", req.change_id),
            thread_id=thread_id,
            results=res.get("results", []),
            feedback=res.get("feedback", ""),
            checkpoint_id=ckpt_id,
            latency_seconds=round(latency, 2),
        )
    except FileNotFoundError as e:
        _append_langgraph_run_log(
            change_id=req.change_id, thread_id=thread_id, status="error", task_count=0,
            latency_seconds=time.time() - start, workspace_root=req.workspace_root,
            project_key=getattr(req, "project_key", None), error=str(e),
        )
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        _append_langgraph_run_log(
            change_id=req.change_id, thread_id=thread_id, status="error", task_count=0,
            latency_seconds=time.time() - start, workspace_root=req.workspace_root,
            project_key=getattr(req, "project_key", None), error=str(e),
        )
        raise HTTPException(status_code=500, detail=str(e))


# 内存缓存：thread_id -> 最近一次 state 快照（MVP 用于 /status）
_status_cache: dict[str, dict] = {}


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
