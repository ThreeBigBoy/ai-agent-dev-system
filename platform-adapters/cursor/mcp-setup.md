## Cursor MCP 接线说明（mcp-setup）

本文件说明如何在 Cursor 中通过 **MCP（Model Context Protocol）** 将 `agent_team_project/` 注册为名为 `agent-team` 的 server，从而实现 `decision_sink` 与 Cursor 宿主下的运行目录绑定。

### 1. 目标

- 让主 Agent 可以通过 MCP 工具（如 `write_decision`）把结构化决策写入运行后端可读取的位置（decision_sink）。  
- 按 Cursor 当前使用约束，将 `AGENT_TEAM_PROJECT_ROOT` 绑定到 `agent_team_project/` 目录。

### 2. 配置模板

在本仓库中提供了一个模板文件：

- `platform-adapters/cursor/mcp.template.json`

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
