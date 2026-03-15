## Cursor MCP 接线说明（mcp-setup）

本文件说明如何在 Cursor 中通过 **MCP（Model Context Protocol）** 将 `agent_team_project/` 注册为名为 `agent-team` 的 server，从而实现 `decision_sink` 与 Cursor 宿主下的运行目录绑定。

### 1. 目标

- 让主 Agent 可以通过 MCP 工具（如 `write_decision`）把结构化决策写入运行后端可读取的位置（decision_sink）。  
- 按 Cursor 当前使用约束，将 `AGENT_TEAM_PROJECT_ROOT` 绑定到 `agent_team_project/` 目录。

### 2. 配置模板

在本仓库中提供了一个模板文件：

- `platform-adapters/cursor/mcp.template.json`

**说明**：其中的 `agent-team`（`agent_team_mcp_server.py`）已标记为 **deprecated**，推荐改用 **langgraph-backend**（见第 6 节）与 [agent_team_project/MIGRATION.md](../../agent_team_project/MIGRATION.md)。兼容期约 1 个月。

内容示例如下（请根据本机路径修改 `ABS/PATH` 部分）：

```json
{
  "mcpServers": {
    "agent-team": {
      "command": "python3",
      "args": [
        "/ABS/PATH/TO/ai-agent-dev-system/agent_team_project/agent_team_mcp_server.py"
      ],
      "env": {
        "AGENT_TEAM_PROJECT_ROOT": "/ABS/PATH/TO/ai-agent-dev-system/agent_team_project",
        "AGENT_HOST_TYPE": "cursor"
      }
    }
  }
}
```

### 3. 应用到本机配置

1. 打开本机的 Cursor MCP 配置文件：  
   - 一般路径为：`~/.cursor/mcp.json`（以当前 Cursor 版本为准）。  
2. 将模板中的 `agent-team` 配置块复制到你的 `mcp.json` 中：  
   - 修改 `agent_team_mcp_server.py` 的绝对路径，使其指向你本地的 `ai-agent-dev-system/agent_team_project/`。  
   - 将 `AGENT_TEAM_PROJECT_ROOT` 设置为 `ai-agent-dev-system/agent_team_project` 的绝对路径。  
   - 将 `AGENT_HOST_TYPE` 设置为 `cursor`，用于让运行后端识别当前宿主属于白名单宿主。  
3. 保存文件并重启 Cursor，使 MCP 配置生效。

### 4. 语义说明

- `command: "python3"`：推荐统一使用 `python3`，避免未安装 `python` 命令导致找不到解释器。  
- `AGENT_TEAM_PROJECT_ROOT`：对 **Cursor adapter** 而言，当前实际绑定值应为 `ai-agent-dev-system/agent_team_project` 的目录路径。  
  - 这是当前 Cursor 2.0 主流程与本机 `~/.cursor/mcp.json` 配置的实际运行约束。  
  - 不同宿主应优先遵循各自官方文档与适配方式，不要求复用这一绑定值。
- `AGENT_HOST_TYPE`：建议显式设置为 `cursor`。  
  - 运行后端会据此识别当前属于白名单宿主，子 Agent 保持“宿主内置模型优先，异常再降级 API”的策略。

### 5. 与治理内核的关系

- MCP 配置只属于 **宿主接线层**：用于让 Cursor 能调用 `agent_team_project`。  
- 不改变以下治理优先级：  
  1. `OpenSpec.md`  
  2. `global-rules/*.md`  
  3. `agents/*.md`  
  4. `skills/*/SKILL.md`  
  5. `platform-adapters/*/*.md`  
  6. 宿主入口文件（如 `.cursor/rules/*.mdc`、根 `AGENTS.md` 等）  
  7. 运行后端实现（如 `agent_team_project/`）

主 Agent 在做决策时，仍以治理内核为准；`agent-team` MCP 只是其中一个决策下沉与执行的实现方式。

---

### 6. LangGraph 独立后端（langgraph-backend）

若已实现 `agent_team_project/langgraph_backend/` 与 `langgraph_mcp_server.py`，可增加 **langgraph-backend** MCP 服务，供 Cursor 通过工具调用 LangGraph 后端（HTTP `POST /run` 等）：

- **工具**：`run_langgraph(change_id, task_range?, workspace_root?)`、`resume_langgraph(change_id, thread_id, checkpoint_id)`（断点续跑）、`get_langgraph_status(change_id)`、`langgraph_health()`。  
  - **优先本仓**：后端始终先读本仓 `openspec/changes/`，再试业务项目。  
  - **业务项目配置**（二选一，均在 `langgraph-backend.env`）：  
    1) **JSON 数组**（推荐多项目）：`LANGGRAPH_WORKSPACE_PROJECTS` 为 JSON 字符串，如  
       `"[{\"LANGGRAPH_PROJECT_KEY\":\"Proj01ShopifyTheme\",\"LANGGRAPH_WORKSPACE_ROOT\":\"/path/Proj01\"},{...}]"`；  
       仅此一项即可，后端按 change_id 在列表中自动解析；可选 **`LANGGRAPH_CURRENT_PROJECT_KEY`** 指定当前项目 key 时只使用该项目根。  
    2) **扁平串**：`LANGGRAPH_WORKSPACE_PROJECTS` = `"key1|path1:key2|path2"`，同样按 change_id 自动解析；可选 current key 固定当前项目。  
  - **仅在本仓**迭代时：不设或留空上述配置即可。**兼容**：可仍用 **`LANGGRAPH_WORKSPACE_ROOT`** 单路径。
- **留痕**：每次执行自动写入 `ai-agent-dev-system/runtime-logs/langgraph-runs/YYYY-MM-DD.jsonl`，不依赖迭代日志或 design/documents。
- **前提**：先单独启动后端服务（如 `cd agent_team_project && source .venv/bin/activate && uvicorn langgraph_backend.server:app --port 8000`），再在 Cursor 中调用上述 MCP 工具。
- 在 `mcp.template.json` 中已包含 `langgraph-backend` 条目；将模板中的 `/ABS/PATH/TO/ai-agent-dev-system` 替换为本机路径后合并到 `~/.cursor/mcp.json` 即可。
- **`AGENT_HOST_TYPE`**：建议在 `langgraph-backend.env` 中显式设置为 `cursor`，便于多宿主场景下运行后端识别当前宿主并选用对应模型策略；其他宿主见各 adapter 文档（如 Continue / OpenAI-Codex）。
- 运行 `langgraph_mcp_server.py` 需已安装 `mcp`（与 `agent-team` 相同）：`pip install mcp`。
- **超时**：调用 `/run`、`/resume` 的 HTTP 超时默认 300 秒；可通过环境变量 `LANGGRAPH_HTTP_TIMEOUT`（秒）覆盖。任务数较多时可适当调大或分段执行。

**多业务项目配置完整示例**：
```json
{
  "mcpServers": {
    "langgraph-backend": {
      "command": "python3",
      "args": [
        "/ABS/PATH/TO/ai-agent-dev-system/agent_team_project/langgraph_mcp_server.py"
      ],
      "env": {
        "AGENT_HOST_TYPE": "cursor",
        "LANGGRAPH_WORKSPACE_PROJECTS": "[{\"LANGGRAPH_PROJECT_KEY\":\"Proj01ShopifyTheme\",\"LANGGRAPH_WORKSPACE_ROOT\":\"/ABS/PATH/TO/Proj01ShopifyTheme\"},{\"LANGGRAPH_PROJECT_KEY\":\"test_bizproject\",\"LANGGRAPH_WORKSPACE_ROOT\":\"/ABS/PATH/TO/test_bizproject\"}]"
      }
    }
  }
}
```
- 后端始终**先读本仓**（ai-agent-dev-system/openspec/changes/），若找不到该 change_id，再按列表顺序尝试每个业务项目
- 第一个存在 `openspec/changes/{change_id}/tasks.md` 的项目即命中
- 留痕中会记录命中的 `project_key` 和 `workspace_root`
