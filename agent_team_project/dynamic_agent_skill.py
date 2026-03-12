import os
import json
import logging
import sys
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel, Field

try:
    from langchain.prompts import ChatPromptTemplate
except ImportError:
    from langchain_core.prompts import ChatPromptTemplate

try:
    from langchain.schema import StrOutputParser
except ImportError:
    from langchain_core.output_parsers import StrOutputParser

from runtime_config import load_runtime_config

# 先解析 BASE_DIR，再配置日志与路径，保证所有产物落在脚本所在目录
BASE_DIR = Path(__file__).resolve().parent

# 配置日志（固定写入 agent_team_project，不随 cwd 变化）
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(BASE_DIR / "agent_skill.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("DynamicAgentSkill")

# 加载环境变量
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE_URL = (os.getenv("OPENAI_API_BASE_URL") or "").strip() or None
RUNTIME_CONFIG = load_runtime_config()
EXECUTORS = RUNTIME_CONFIG["executors"]
BACKEND_NAME = RUNTIME_CONFIG["backend_name"]


@dataclass
class ModelCandidate:
    provider: str
    model_name: str
    mode: str = ""


def _workspace_root() -> Path | None:
    root = os.environ.get("AGENT_TEAM_PROJECT_ROOT", "").strip()
    if root and Path(root).is_dir():
        return Path(root)
    return None


def _current_host_type() -> str:
    env_host = os.environ.get("AGENT_HOST_TYPE", "").strip().lower()
    if env_host:
        return env_host
    return (
        RUNTIME_CONFIG.get("host_policy", {})
        .get("default_host", "cursor")
        .strip()
        .lower()
    )


def _feedback_output_paths() -> list[Path]:
    roots = []
    workspace_root = _workspace_root()
    if workspace_root:
        roots.append(workspace_root)
    roots.append(BASE_DIR)
    paths = []
    for root in roots:
        paths.append(root / "agent_feedback.txt")
    deduped = []
    seen = set()
    for path in paths:
        if path in seen:
            continue
        seen.add(path)
        deduped.append(path)
    return deduped


def _write_feedback(content: str) -> None:
    for path in _feedback_output_paths():
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

# --------------------------
# 1. 定义LangGraph状态模型（存储协作全量信息）
# --------------------------
class AgentState(BaseModel):
    task_complexity: str = Field(description="任务复杂度：简单/中等/复杂")
    task_list: list[dict] = Field(description="子任务列表")
    task_results: dict = Field(default={}, description="已完成任务结果")
    feedbacks: list[str] = Field(default=[], description="执行反馈")
    need_adjust: bool = Field(default=False, description="是否需要调整任务")
    adjust_instruction: str = Field(default="", description="调整指令")

# --------------------------
# 2. 定义下游执行Agent（产品/架构/前端/后端/测试）
# --------------------------
def _make_api_llm(model_name: str):
    if not OPENAI_API_KEY:
        raise RuntimeError("未配置 OPENAI_API_KEY，无法使用 API 模型链路")
    kwargs = {
        "model_name": model_name,
        "temperature": RUNTIME_CONFIG["llm"]["temperature"],
        "api_key": OPENAI_API_KEY,
        "timeout": RUNTIME_CONFIG["llm"]["timeout_seconds"],
    }
    if OPENAI_API_BASE_URL:
        kwargs["base_url"] = OPENAI_API_BASE_URL
    return ChatOpenAI(**kwargs)


def _build_model_candidates(task_complexity: str) -> list[ModelCandidate]:
    strategy = RUNTIME_CONFIG["model_strategy"]
    host_policy = RUNTIME_CONFIG.get("host_policy", {})
    provider_policy = host_policy.get("subagent_provider_policy", {})
    current_host = _current_host_type()
    candidates: list[ModelCandidate] = []
    scene = "complex" if task_complexity in ["中等", "复杂"] else "simple"
    order = provider_policy.get("default", "builtin_first")

    if current_host in provider_policy.get("api_first_hosts", []):
        order = "api_first"
    elif current_host in provider_policy.get("builtin_first_hosts", []):
        order = "builtin_first"

    def append_builtin() -> None:
        if strategy.get("cursor_builtin", {}).get("enabled", False):
            candidates.append(
                ModelCandidate(
                    provider="cursor_builtin",
                    model_name="Cursor 内置模型",
                    mode=strategy["cursor_builtin"].get("mode", "Auto"),
                )
            )

    def append_api() -> None:
        if strategy.get("api", {}).get("enabled", False):
            for model_name in strategy["api"]["models"][scene]:
                candidates.append(ModelCandidate(provider="api", model_name=model_name))

    if order == "api_first":
        append_api()
    else:
        append_builtin()
        append_api()

    logger.info("当前宿主类型=%s，子Agent模型链路策略=%s", current_host, order)

    return candidates


def _invoke_with_candidate(prompt, payload: dict, candidate: ModelCandidate, output_parser: StrOutputParser) -> str:
    if candidate.provider == "cursor_builtin":
        # 当前运行时 backend 尚未接入 Cursor 内置模型的官方/稳定桥接能力。
        raise RuntimeError(
            f"未接入 Cursor 内置模型桥接器（模式: {candidate.mode}），按策略降级到 API 链路"
        )

    if candidate.provider == "api":
        llm = _make_api_llm(candidate.model_name)
        chain = prompt | llm | output_parser
        return chain.invoke(payload)

    raise RuntimeError(f"未知模型提供方：{candidate.provider}")


def _build_executor_agents(task_complexity: str) -> dict[str, "ExecutorAgent"]:
    return {executor: ExecutorAgent(executor, task_complexity) for executor in EXECUTORS}


def _normalize_task_results(task_results: dict) -> dict[str, str]:
    normalized = {}
    for key, value in task_results.items():
        normalized[str(key)] = value
    return normalized


def _build_task_meta(task_list: list[dict]) -> dict[str, dict]:
    return {str(task["task_id"]): task for task in task_list}

class ExecutorAgent:
    def __init__(self, role: str, task_complexity: str):
        self.role = role
        self.task_complexity = task_complexity
        self.output_parser = StrOutputParser()

    def run_task(self, task_id: str, task_name: str, input_content: str) -> tuple[str, str]:
        """执行任务并返回结果+反馈（无问题反馈为"无"）。task_id 用于产出文件名 task_{task_id}_{role}.txt"""
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", f"你是资深{self.role}，专业能力极强。执行任务后需判断是否有问题，输出1句话反馈（无问题则填'无'）。"),
                ("user", f"任务名称：{task_name}\n输入要求：{input_content}\n输出格式：先输出完整的任务结果，换行后单独输出【反馈】：你的反馈内容")
            ])
            raw_result = None
            errors = []
            for candidate in _build_model_candidates(self.task_complexity):
                try:
                    logger.info(
                        "尝试模型链路: provider=%s model=%s mode=%s",
                        candidate.provider,
                        candidate.model_name,
                        candidate.mode or "-",
                    )
                    raw_result = _invoke_with_candidate(
                        prompt,
                        {"input": input_content},
                        candidate,
                        self.output_parser,
                    )
                    logger.info(
                        "模型链路成功: provider=%s model=%s",
                        candidate.provider,
                        candidate.model_name,
                    )
                    break
                except Exception as candidate_error:
                    error_text = f"{candidate.provider}:{candidate.model_name} -> {candidate_error}"
                    errors.append(error_text)
                    logger.warning("模型链路失败，尝试降级: %s", error_text)

            if raw_result is None:
                raise RuntimeError("；".join(errors) or "未找到可用模型链路")

            if "【反馈】：" in raw_result:
                result, feedback = raw_result.split("【反馈】：", 1)
            else:
                result = raw_result
                feedback = "无"

            snap_path = BASE_DIR / f"task_{task_id}_{self.role}.txt"
            snap_path.write_text(result, encoding="utf-8")

            logger.info(f"{self.role}完成任务：{task_name}，反馈：{feedback}")
            return result.strip(), feedback.strip()
        except Exception as e:
            error_msg = f"执行失败：{str(e)}"
            logger.error(f"{self.role}执行任务{task_name}失败：{error_msg}")
            return "", error_msg

# --------------------------
# 3. 定义LangGraph节点逻辑（动态协作核心）
# --------------------------
def execute_tasks(state: AgentState) -> AgentState:
    executor_agents = _build_executor_agents(state.task_complexity)
    new_feedbacks = []
    new_task_results = _normalize_task_results(state.task_results.copy())

    for task in sorted(state.task_list, key=lambda x: x["task_id"]):
        task_id = str(task["task_id"])
        executor = task["executor"]
        if task_id in new_task_results:
            # 已有结果（含历史加载），跳过执行，但补写快照以便本轮回显与「生成文件列表」一致
            snap_path = BASE_DIR / f"task_{task_id}_{executor}.txt"
            try:
                snap_path.write_text(new_task_results[task_id] or "", encoding="utf-8")
                logger.info(f"已补写快照（跳过执行）：{snap_path}")
            except OSError as e:
                logger.warning(f"补写快照失败 {snap_path}: {e}")
            continue
        if executor not in executor_agents:
            error_msg = f"未配置的执行角色：{executor}"
            logger.error(error_msg)
            new_task_results[task_id] = ""
            new_feedbacks.append(f"任务{task_id}（{executor}）：{error_msg}")
            continue
        input_content = task["input_requirement"]
        for dep_id in str(task["dependency"]).split(","):
            dep_id = dep_id.strip()
            if dep_id != "0" and dep_id in new_task_results:
                input_content += f"\n\n依赖任务{dep_id}结果：\n{new_task_results[dep_id]}"
        result, feedback = executor_agents[executor].run_task(str(task["task_id"]), task["task_name"], input_content)
        new_task_results[task_id] = result
        if feedback and feedback != "无":
            new_feedbacks.append(f"任务{task_id}（{executor}）：{feedback}")

    state.task_results = new_task_results
    state.feedbacks = new_feedbacks
    state.need_adjust = len(new_feedbacks) > 0
    return state

def check_feedback(state: AgentState) -> str:
    if state.need_adjust:
        logger.info(f"检测到{len(state.feedbacks)}条反馈，需要调整任务")
        return "adjust_tasks"
    logger.info("无有效反馈，任务执行完成")
    return "end"

def adjust_tasks(state: AgentState) -> AgentState:
    feedback_summary = "\n".join(state.feedbacks)
    state.adjust_instruction = f"""
### 任务执行反馈（需调整）
{feedback_summary}

请作为总指挥，根据以上反馈调整任务分工：
1. 补充/修改相关子任务（保持原JSON格式）
2. 输出新的任务分工JSON，覆盖写入agent_decision.json
3. 无需额外解释，仅输出JSON
    """
    logger.info(f"生成调整指令：{state.adjust_instruction[:100]}...")
    return state

# --------------------------
# 4. 构建LangGraph动态协作图
# --------------------------
def build_dynamic_graph() -> CompiledStateGraph:
    graph = StateGraph(AgentState)
    graph.add_node("execute_tasks", execute_tasks)
    graph.add_node("adjust_tasks", adjust_tasks)
    graph.add_node("end", lambda x: x)
    graph.set_entry_point("execute_tasks")
    graph.add_conditional_edges("execute_tasks", check_feedback, {"adjust_tasks": "adjust_tasks", "end": "end"})
    graph.add_edge("adjust_tasks", END)
    graph.add_edge("end", END)
    return graph.compile()

# --------------------------
# 5. Skill核心执行函数
# --------------------------
def _clear_previous_task_snapshots() -> None:
    """清理本轮运行前的 task_*.txt 快照（在 BASE_DIR 下），避免目录下文件持续累积。"""
    for f in BASE_DIR.glob("task_*.txt"):
        try:
            f.unlink()
            logger.info(f"已清理旧快照：{f.name}")
        except OSError as e:
            logger.warning(f"清理快照失败 {f}: {e}")


def run_dynamic_agent_team(manager_decision_json: str) -> str:
    try:
        _clear_previous_task_snapshots()
        raw = (manager_decision_json or "").strip()
        if not raw:
            raise ValueError("决策内容为空，请先通过 MCP write_decision 写入 agent_decision.json")
        manager_decision = json.loads(raw)
        matched_scene = manager_decision.get("matched_scene", "scene3-other")
        decision_reason = (manager_decision.get("reason") or "").strip()
        logger.info(
            "接收到运行决策：任务复杂度=%s，场景=%s，子任务数=%s，判定理由=%s",
            manager_decision.get("task_complexity"),
            matched_scene,
            len(manager_decision.get("task_list", [])),
            decision_reason or "（未提供）",
        )
        initial_state = AgentState(
            task_complexity=manager_decision["task_complexity"],
            task_list=manager_decision["task_list"]
        )
        state_file = BASE_DIR / "agent_state.json"
        if state_file.exists():
            try:
                raw_state = state_file.read_text(encoding="utf-8").strip()
                if raw_state:
                    history_state = json.loads(raw_state)
                    initial_state.task_results = _normalize_task_results(history_state.get("task_results", {}))
                    logger.info("加载历史协作状态，跳过已完成任务")
            except (json.JSONDecodeError, OSError) as e:
                logger.warning(f"agent_state.json 为空或无效，将视为无历史状态：{e}")
        graph = build_dynamic_graph()
        final_state = graph.invoke(initial_state)
        # LangGraph 部分版本 invoke 返回 dict，需统一为 AgentState 以便序列化与属性访问
        if isinstance(final_state, dict):
            final_state = AgentState(**final_state)
        with open(BASE_DIR / "agent_state.json", "w", encoding="utf-8") as f:
            f.write(final_state.model_dump_json(ensure_ascii=False, indent=2))
        decision_header = f"Task decision: [complexity={manager_decision.get('task_complexity')}, scene={matched_scene}, reason={decision_reason or '（未提供）'}]"
        if final_state.need_adjust:
            summary = f"""
### 动态协作执行结果（需调整）
{decision_header}
1. 任务复杂度：{final_state.task_complexity}
2. 已完成任务数：{len(final_state.task_results)} / {len(final_state.task_list)}
3. 反馈问题列表：
{json.dumps(final_state.feedbacks, ensure_ascii=False, indent=2)}
"""
        else:
            task_meta = _build_task_meta(final_state.task_list)
            generated_files = [
                f"task_{task_id}_{task_meta[task_id]['executor']}.txt"
                for task_id in sorted(final_state.task_results.keys(), key=int)
                if task_id in task_meta
            ]
            summary = f"""
### 动态协作执行结果（完成）
{decision_header}
0. 运行后端：{BACKEND_NAME}
1. 任务复杂度：{final_state.task_complexity}
2. 总任务数：{len(final_state.task_list)}
3. 已完成任务数：{len(final_state.task_results)}
4. 生成文件列表：{generated_files}
5. 所有任务执行完成，无需调整。
"""
        _write_feedback(summary)
        logger.info(f"执行结果已写入反馈文件：{_feedback_output_paths()}")
        return summary
    except json.JSONDecodeError as e:
        error_msg = f"决策 JSON 解析失败：{str(e)}（请确认 agent_decision.json 内容完整且为合法 JSON）"
        logger.error(error_msg)
        _write_feedback(f"执行失败：{error_msg}")
        return error_msg
    except ValueError as e:
        error_msg = str(e)
        logger.error(error_msg)
        _write_feedback(f"执行失败：{error_msg}")
        return error_msg
    except Exception as e:
        error_msg = f"动态协作执行失败：{str(e)}"
        logger.error(error_msg)
        _write_feedback(f"执行失败：{error_msg}")
        return error_msg

# --------------------------
# 6. 脚本入口
# --------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("用法：python3 dynamic_agent_skill.py <决策JSON字符串或 agent_decision.json 的路径>")
        sys.exit(1)
    arg = sys.argv[1].strip()
    # 若参数为已存在文件路径，则从文件读取，避免命令行长度与转义问题
    if Path(arg).is_file():
        manager_decision_json = Path(arg).read_text(encoding="utf-8")
        logger.info(f"从文件读取决策：{arg}")
    else:
        manager_decision_json = arg
    result = run_dynamic_agent_team(manager_decision_json)
    print(result)
