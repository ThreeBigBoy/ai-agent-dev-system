"""7 个 executor 的执行逻辑：单任务调用 API 模型，返回规范结果。"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

# 运行根目录约定：需从 agent_team_project 根加载 runtime_config，故将根加入 sys.path。
# 请以 agent_team_project 为工作目录启动（或确保 PYTHONPATH 含该根），避免依赖全局 sys.path 副作用。
# 若需隔离，可改为通过环境变量指定配置路径并用 importlib 加载。
_AGENT_ROOT = Path(__file__).resolve().parent.parent
if str(_AGENT_ROOT) not in sys.path:
    sys.path.insert(0, str(_AGENT_ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(_AGENT_ROOT / ".env")
except Exception:
    pass

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from runtime_config import load_runtime_config

# 可选：使用 OpenAI 兼容 API
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    ChatOpenAI = None

RUNTIME_CONFIG = load_runtime_config()
EXECUTORS = set(RUNTIME_CONFIG.get("executors", []))


def _make_llm():
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = (os.getenv("OPENAI_API_BASE_URL") or "").strip() or None
    if not api_key:
        raise RuntimeError("未配置 OPENAI_API_KEY")
    models = RUNTIME_CONFIG.get("model_strategy", {}).get("api", {}).get("models", {}).get("complex", ["Pro/deepseek-ai/DeepSeek-V3.2"])
    model_name = models[0] if models else "Pro/deepseek-ai/DeepSeek-V3.2"
    kwargs = {
        "model": model_name,
        "temperature": RUNTIME_CONFIG.get("llm", {}).get("temperature", 0.1),
        "api_key": api_key,
        "timeout": RUNTIME_CONFIG.get("llm", {}).get("timeout_seconds", 60),
    }
    if base_url:
        kwargs["base_url"] = base_url
    return ChatOpenAI(**kwargs)


def run_one_task(executor: str, task_id: int, task_name: str, input_requirement: str) -> dict:
    """
    执行单任务，返回 design 4.3 的 Executor Result。
    若 executor 不在 7 人列表（如 主 Agent），返回 status=success 的占位结果。
    """
    start = time.time()
    if executor not in EXECUTORS:
        return {
            "task_id": task_id,
            "executor": executor,
            "status": "success",
            "output": f"（{executor} 为治理角色，本后端不执行具体任务）",
            "feedback": "无",
            "latency_ms": int((time.time() - start) * 1000),
        }
    try:
        if ChatOpenAI is None:
            raise RuntimeError("未安装 langchain-openai")
        llm = _make_llm()
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"你是资深{executor}，专业能力极强。执行任务后需判断是否有问题，输出1句话反馈（无问题则填'无'）。"),
            ("user", "任务名称：{task_name}\n输入要求：{input_requirement}\n输出格式：先输出完整的任务结果，换行后单独输出【反馈】：你的反馈内容"),
        ])
        chain = prompt | llm | StrOutputParser()
        raw = chain.invoke({"task_name": task_name, "input_requirement": input_requirement})
        if "【反馈】：" in raw:
            output, feedback = raw.split("【反馈】：", 1)
        else:
            output, feedback = raw.strip(), "无"
        return {
            "task_id": task_id,
            "executor": executor,
            "status": "success",
            "output": output.strip(),
            "feedback": feedback.strip(),
            "latency_ms": int((time.time() - start) * 1000),
        }
    except Exception as e:
        return {
            "task_id": task_id,
            "executor": executor,
            "status": "error",
            "output": "",
            "feedback": str(e),
            "latency_ms": int((time.time() - start) * 1000),
        }
