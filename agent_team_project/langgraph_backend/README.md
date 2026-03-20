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
- `parser.py`：从 `openspec/changes/{change_id}/tasks.md` 解析任务，生成决策对象；**V2.11.2+** 解析出 0 条任务时返回 `parse_format_hint` 格式诊断（章节缺 Executor、任务行 **N.M** 等）
- `executors.py`：7 个 executor 单任务执行（调用 API 模型）
- `workflow.py`：StateGraph 定义（parse_tasks → dispatch → collect_feedback），MemorySaver 检查点；**V2.11.2+** 解析到 0 条任务时默认 `blocked` 并带格式提示，请求可传 `allow_zero_tasks=true` 放行治理类 run
- `server.py`：FastAPI 服务，/run、/status、/health、/resume（断点续跑）；**V2.11.2+** RunRequest 支持 `allow_zero_tasks`，RunResponse 返回 `total_tasks`、`tasks_format_hint` 便于迭代日志与诊断
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

## 仓库根自检与冒烟脚本（不在本进程内自动执行）

`langgraph_backend` 服务进程、MCP `langgraph_mcp_server.py` **均不会**自动调用下列脚本。它们位于 **ai-agent-dev-system 仓库根**的 `scripts/` 下，供你在本机终端**手动**或 **CI** 中做环境检查、管线最小验证、HTTP 冒烟与「一键自检」。

| 脚本目录 | 作用摘要 | 文档 |
|----------|----------|------|
| [`scripts/diagnose_startup/`](../../scripts/diagnose_startup/) | 启动前环境诊断（磁盘 / Python / 内存 / 网络 / 配置 / 端口等） | [README.md](../../scripts/diagnose_startup/README.md) |
| [`scripts/verify-minimal/`](../../scripts/verify-minimal/) | 最小管线验证：先跑诊断，再本地 `invoke` workflow（HC0/HC7 场景），可选请求 `/health` 与 `/confirm/pending` | [README.md](../../scripts/verify-minimal/README.md) |
| [`scripts/smoke-http/`](../../scripts/smoke-http/) | 后端**已启动**时，用 `curl` 打 `/health`、`/run`、`/confirm/*` 做快速冒烟 | [README.md](../../scripts/smoke-http/README.md) |
| [`scripts/check-langgraph-backend/`](../../scripts/check-langgraph-backend/) | 一键自检：`/health`、`AGENT_TEAM_PROJECT_ROOT`、解析 `~/.cursor/mcp.json` 中工作区、对本仓/业务 `change_id` 调 `/run` 并查留痕 | [README.md](../../scripts/check-langgraph-backend/README.md) |

**`verify-minimal` 与 `check-langgraph-backend` 怎么选**：

- **`verify-minimal`**：侧重 **本机 StateGraph / 门控（如 HC0/HC7）逻辑**——会先跑 `diagnose_startup`，再在进程内 `invoke` workflow；**可不启动 HTTP 服务**就覆盖大部分检查；**不读取** `~/.cursor/mcp.json`，也不按「MCP 多项目根 + 真实留痕文件」做系统性验收。
- **`check-langgraph-backend`**：侧重 **与 Cursor 真链路一致的集成验收**——要求后端已监听 HTTP，走真实 **`POST /run`**，并校验 `AGENT_TEAM_PROJECT_ROOT`、从 **`mcp.json` 解析 `LANGGRAPH_WORKSPACE_PROJECTS`**、核对 `runtime-logs/langgraph-runs/` 等；适合 MCP、多业务仓库根、留痕路径都配好后的**整体验证**。

**对比一句**：前者像「单元 + 本地图跑通」；后者像「按你真实宿主配置打一遍 HTTP 并查日志」。可先后都跑：先 `verify-minimal` 缩小代码/环境问题，再跑一键自检确认 MCP 与多根目录（详见 [`check-langgraph-backend/README.md`](../../scripts/check-langgraph-backend/README.md) 前言与「何时使用」表）。

**从本文件所在目录理解路径**：`langgraph_backend/` 的上一级是 `agent_team_project/`，再上一级即仓库根；上述链接已按相对路径指向 `../../scripts/...`。

更多入口说明见仓库根 [`新用户快速开始.md`](../../新用户快速开始.md)（含 §5.2 启动与验证）、[`scripts/README.md`](../../scripts/README.md)。

## 状态说明

- 状态图内使用 `ckpt_ref` 代替 `checkpoint_id`，避免与 LangGraph 保留通道名冲突。
- POST /resume 已实现：传入 change_id、thread_id、checkpoint_id（/run 返回）可从检查点恢复执行；MCP 工具 `resume_langgraph` 可调用。
