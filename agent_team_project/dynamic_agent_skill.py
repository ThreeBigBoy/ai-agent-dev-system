import os
import json
import logging
import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from pydantic import BaseModel, Field

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("agent_skill.log"), logging.StreamHandler()]
)
logger = logging.getLogger("DynamicAgentSkill")

# 加载环境变量
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_BASE_URL = (os.getenv("OPENAI_API_BASE_URL") or "").strip() or None
if not OPENAI_API_KEY:
    logger.error("未配置OPENAI_API_KEY，请检查.env文件")
    sys.exit(1)

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
def _make_llm(task_complexity: str):
    kwargs = {
        "model_name": "gpt-4-turbo" if task_complexity in ["中等", "复杂"] else "gpt-3.5-turbo",
        "temperature": 0.1,
        "api_key": OPENAI_API_KEY,
        "timeout": 60,
    }
    if OPENAI_API_BASE_URL:
        kwargs["base_url"] = OPENAI_API_BASE_URL
    return ChatOpenAI(**kwargs)

class ExecutorAgent:
    def __init__(self, role: str, task_complexity: str):
        self.role = role
        self.llm = _make_llm(task_complexity)
        self.output_parser = StrOutputParser()

    def run_task(self, task_name: str, input_content: str) -> tuple[str, str]:
        """执行任务并返回结果+反馈（无问题反馈为"无"）"""
        try:
            prompt = ChatPromptTemplate.from_messages([
                ("system", f"你是资深{self.role}，专业能力极强。执行任务后需判断是否有问题，输出1句话反馈（无问题则填'无'）。"),
                ("user", f"任务名称：{task_name}\n输入要求：{input_content}\n输出格式：先输出完整的任务结果，换行后单独输出【反馈】：你的反馈内容")
            ])
            chain = prompt | self.llm | self.output_parser
            raw_result = chain.invoke({"input": input_content})

            if "【反馈】：" in raw_result:
                result, feedback = raw_result.split("【反馈】：", 1)
            else:
                result = raw_result
                feedback = "无"

            task_id = task_name.split("-")[0] if "-" in task_name else "unknown"
            with open(f"task_{task_id}_{self.role}.txt", "w", encoding="utf-8") as f:
                f.write(result)

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
    executor_agents = {
        "产品经理": ExecutorAgent("产品经理", state.task_complexity),
        "架构师": ExecutorAgent("架构师", state.task_complexity),
        "前端工程师": ExecutorAgent("前端工程师", state.task_complexity),
        "后端工程师": ExecutorAgent("后端工程师", state.task_complexity),
        "测试工程师": ExecutorAgent("测试工程师", state.task_complexity)
    }
    new_feedbacks = []
    new_task_results = state.task_results.copy()

    for task in sorted(state.task_list, key=lambda x: x["task_id"]):
        task_id = task["task_id"]
        if task_id in new_task_results:
            continue
        executor = task["executor"]
        input_content = task["input_requirement"]
        for dep_id in str(task["dependency"]).split(","):
            dep_id = dep_id.strip()
            if dep_id != "0" and dep_id in new_task_results:
                input_content += f"\n\n依赖任务{dep_id}结果：\n{new_task_results[dep_id]}"
        result, feedback = executor_agents[executor].run_task(task["task_name"], input_content)
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
2. 输出新的任务分工JSON，覆盖写入cursor_decision.json
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
def run_dynamic_agent_team(manager_decision_json: str) -> str:
    try:
        manager_decision = json.loads(manager_decision_json.strip())
        logger.info(f"接收到Cursor决策：任务复杂度={manager_decision['task_complexity']}，子任务数={len(manager_decision['task_list'])}")
        initial_state = AgentState(
            task_complexity=manager_decision["task_complexity"],
            task_list=manager_decision["task_list"]
        )
        if os.path.exists("agent_state.json"):
            with open("agent_state.json", "r", encoding="utf-8") as f:
                history_state = json.load(f)
            initial_state.task_results = history_state.get("task_results", {})
            logger.info("加载历史协作状态，跳过已完成任务")
        graph = build_dynamic_graph()
        final_state = graph.invoke(initial_state)
        with open("agent_state.json", "w", encoding="utf-8") as f:
            f.write(final_state.model_dump_json(ensure_ascii=False, indent=2))
        if final_state.need_adjust:
            summary = f"""
### 动态协作执行结果（需调整）
1. 任务复杂度：{final_state.task_complexity}
2. 已完成任务数：{len(final_state.task_results)} / {len(final_state.task_list)}
3. 反馈问题列表：
{json.dumps(final_state.feedbacks, ensure_ascii=False, indent=2)}
"""
        else:
            task_list = final_state.task_list
            summary = f"""
### 动态协作执行结果（完成）
1. 任务复杂度：{final_state.task_complexity}
2. 总任务数：{len(task_list)}
3. 已完成任务数：{len(final_state.task_results)}
4. 生成文件列表：{list(final_state.task_results.keys())}
5. 所有任务执行完成，无需调整。
"""
        with open("cursor_feedback.txt", "w", encoding="utf-8") as f:
            f.write(summary)
        logger.info("执行结果已写入cursor_feedback.txt，插件将读取并复制到剪贴板")
        return summary
    except json.JSONDecodeError as e:
        error_msg = f"JSON解析失败：{str(e)}"
        logger.error(error_msg)
        with open("cursor_feedback.txt", "w", encoding="utf-8") as f:
            f.write(f"执行失败：{error_msg}")
        return error_msg
    except Exception as e:
        error_msg = f"动态协作执行失败：{str(e)}"
        logger.error(error_msg)
        with open("cursor_feedback.txt", "w", encoding="utf-8") as f:
            f.write(f"执行失败：{error_msg}")
        return error_msg

# --------------------------
# 6. 脚本入口
# --------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error("用法：python3 dynamic_agent_skill.py '初始决策JSON字符串'")
        sys.exit(1)
    manager_decision_json = sys.argv[1]
    result = run_dynamic_agent_team(manager_decision_json)
    print(result)
