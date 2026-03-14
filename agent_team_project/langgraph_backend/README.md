# LangGraph 独立后端

多 Agent 协同的编排与执行服务，由 Cursor 等 IDE 通过 MCP 或 HTTP 调用。

## 总体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      Cursor / VS Code                       │
│  ┌─────────────────┐      ┌─────────────────────────────┐  │
│  │   用户消息       │─────▶│   扩展检测 change-id + 关键词  │  │
│  └─────────────────┘      └─────────────────────────────┘  │
│                              │                              │
│                              ▼                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  MCP 工具 / HTTP 调用                                     ││
│  │  POST /run {change_id, task_range?}                    ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTP / JSON
┌─────────────────────────────────────────────────────────────┐
│                  LangGraph 独立后端 (FastAPI)                │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  StateGraph: parse_tasks → dispatch → collect_feedback ││
│  │                                                         ││
│  │  ┌──────────────┐    ┌──────────┐    ┌──────────────┐  ││
│  │  │ parse_tasks  │───▶│ dispatch │───▶│ collect_fb   │  ││
│  │  │ (节点函数)    │    │ (节点函数)│    │ (节点函数)    │  ││
│  │  └──────────────┘    └──────────┘    └──────────────┘  ││
│  │       │                    │                  │         ││
│  │       ▼                    ▼                  ▼         ││
│  │  ┌─────────────────────────────────────────────────────┐││
│  │  │ 检查点 (MemorySaver / Redis)                       │││
│  │  │ state: {change_id, decision, results, feedback}    │││
│  │  └─────────────────────────────────────────────────────┐││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ 调用 7 个 executor
┌─────────────────────────────────────────────────────────────┐
│                    API 模型 (SiliconFlow等)                   │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │ 产品经理 │ │ 架构师   │ │ 前端工程师│ │ 后端工程师│ ...       │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
└─────────────────────────────────────────────────────────────┘
```

## 目录

- `config.py`：工作区根与 openspec 路径
- `parser.py`：从 `openspec/changes/{change_id}/tasks.md` 解析任务，生成决策对象
- `executors.py`：7 个 executor 单任务执行（调用 API 模型）
- `workflow.py`：StateGraph 定义（parse_tasks → dispatch → collect_feedback），MemorySaver 检查点
- `server.py`：FastAPI 服务，/run、/status、/health、/resume（断点续跑）
- `langgraph_mcp_server.py`：MCP 服务端，封装 HTTP 调用为 `run_langgraph` / `resume_langgraph` 工具

## 运行

需设置 `AGENT_TEAM_PROJECT_ROOT` 指向含 `openspec/changes` 的仓库根（如 ai-agent-dev-system）。

**依赖**：执行器（executor）会调用 LLM，需安装 `langchain-openai`（及 `langchain-core`）。一键安装：

```bash
cd agent_team_project
bash setup-langgraph-env.sh   # 创建 .venv 并安装全部依赖（含 langchain-openai）
source .venv/bin/activate
# 或：pip install -r requirements.txt
```

启动服务：

```bash
cd agent_team_project
source .venv/bin/activate
uvicorn langgraph_backend.server:app --reload --port 8000
```

健康检查：`GET http://localhost:8000/health`  
执行：`POST http://localhost:8000/run` Body: `{"change_id": "migrate-langgraph-backend", "task_range": "2.1-2.2"}`

## Cursor 联调（任务 3.4）

1. **启动后端**（终端 1）  
   `cd agent_team_project && source .venv/bin/activate && AGENT_TEAM_PROJECT_ROOT=/path/to/ai-agent-dev-system uvicorn langgraph_backend.server:app --port 8000`

2. **配置 MCP**  
   将 `platform-adapters/cursor/mcp.template.json` 中的 `langgraph-backend` 块合并到 `~/.cursor/mcp.json`，把 `/ABS/PATH/TO/ai-agent-dev-system` 换成实际路径。业务项目多根配置（`LANGGRAPH_WORKSPACE_PROJECTS` 等）见 `platform-adapters/cursor/mcp-setup.md` §6。重启 Cursor。

3. **在 Cursor 中调用**  
   在对话中说「请用 run_langgraph 工具执行 change_id = migrate-langgraph-backend」或指定 task_range（如 "2.1-2.2"）；主 Agent 会调用 MCP 工具，工具返回的格式化结果会出现在对话中。

4. **验收**  
   Cursor → MCP（run_langgraph）→ HTTP /run → 后端执行 → 返回 feedback/results → 展示在 Chat。

## 状态说明

- 状态图内使用 `ckpt_ref` 代替 `checkpoint_id`，避免与 LangGraph 保留通道名冲突。
- POST /resume 已实现：传入 change_id、thread_id、checkpoint_id（/run 返回）可从检查点恢复执行；MCP 工具 `resume_langgraph` 可调用。
