"""
人工确认节点 MCP 接口约定 (P1-A2)
供前端 / MCP 客户端调用：approve / reject / comment。
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class HumanConfirmRequest:
    """等待人工确认时的请求体（服务端→客户端或 Long Poll 响应）"""
    hc_id: str                    # HC1 | HC2 | HC3 | HC4 | HC7
    change_id: str
    step_name: str                # step2.5_prd | step4.5_design | step7.5_acceptance
    context_summary: str
    artifacts: List[str]          # 待确认产出物路径列表
    request_id: str               # 唯一请求 ID，提交时回传
    timeout_seconds: int = 3600


@dataclass
class HumanConfirmResponse:
    """提交人工确认结果（客户端→服务端）"""
    request_id: str
    hc_id: str
    change_id: str
    decision: str                 # "approve" | "reject" | "comment"
    comment: Optional[str] = None
    reviewer: str = ""
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.decision not in ("approve", "reject", "comment"):
            raise ValueError("decision must be approve | reject | comment")
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


# MCP 工具名约定（供 MCP Server 注册）
MCP_TOOL_HUMAN_CONFIRM_SUBMIT = "human_confirm_submit"   # 提交确认结果
MCP_TOOL_HUMAN_CONFIRM_POLL = "human_confirm_poll"      # 轮询待确认列表（可选）
