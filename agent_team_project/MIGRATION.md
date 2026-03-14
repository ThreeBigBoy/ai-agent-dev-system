# 从旧机制迁移到 LangGraph 独立后端

本文说明如何从基于 **agent_decision.json + 文件监听 + agent_team_mcp_server.py** 的旧机制，迁移到 **LangGraph 独立后端**（`langgraph_backend/` + `langgraph_mcp_server.py`）。

---

## 1. 为何迁移

| 对比项       | 旧机制（deprecated）                         | 新机制（LangGraph 后端）                    |
|--------------|----------------------------------------------|---------------------------------------------|
| 触发方式     | 主 Agent 写 `agent_decision.json`，文件监听或 MCP `write_decision` 触发 | 主 Agent 直接调用 MCP `run_langgraph(change_id)`，**调用即执行** |
| 竞态         | 文件监听与 MCP 可能同时触发，易重复执行     | 无文件监听，单一路径，无竞态                |
| 状态与断点   | 依赖本地文件，无标准断点续跑                 | 检查点持久化，支持 `resume_langgraph` 断点续跑 |
| 决策载体     | `agent_decision.json` 文件                   | 后端从 `openspec/changes/{change_id}/tasks.md` 解析，无需手写 JSON |

---

## 2. 兼容期约定（5.3）

- **兼容期**：自本迁移指南发布起约 **1 个月** 内，旧机制（`agent_team_mcp_server.py`、`dynamic_agent_skill.py`、基于 `agent_decision.json` 的文件监听）仍可正常使用，但已标记为 **deprecated**。
- **推荐**：新配置与现有用户均建议在本期限内完成迁移；到期后旧机制可能不再维护，仅保留新后端路径。

---

## 3. 迁移步骤（新用户或从零配置）

### 3.1 环境准备

- Python 3.10+，建议使用虚拟环境：
  ```bash
  cd agent_team_project
  python3 -m venv .venv
  source .venv/bin/activate   # Windows: .venv\Scripts\activate
  pip install langgraph fastapi uvicorn langchain-openai pydantic python-multipart mcp
  ```
- 设置 `AGENT_TEAM_PROJECT_ROOT` 指向**含 `openspec/changes` 的仓库根**（即 ai-agent-dev-system 根目录），例如：
  ```bash
  export AGENT_TEAM_PROJECT_ROOT="/你的路径/ai-agent-dev-system"
  ```

### 3.2 启动 LangGraph 后端

在 `agent_team_project` 目录下：

```bash
AGENT_TEAM_PROJECT_ROOT="/你的路径/ai-agent-dev-system" uvicorn langgraph_backend.server:app --host 127.0.0.1 --port 8000
```

保持该终端运行，或以后台方式启动。健康检查：`curl http://127.0.0.1:8000/health` 应返回 `{"status":"healthy",...}`。

### 3.3 配置 Cursor MCP（使用新后端）

1. 打开 `~/.cursor/mcp.json`（或合并自本仓库 `platform-adapters/cursor/mcp.template.json`）。
2. 添加 **langgraph-backend** 服务（将 `ABS/PATH` 换成本机路径）：
   ```json
   "langgraph-backend": {
     "command": "python3",
     "args": ["/ABS/PATH/ai-agent-dev-system/agent_team_project/langgraph_mcp_server.py"]
   }
   ```
3. 保存并重启 Cursor，使新 MCP 生效。

详细说明见 [platform-adapters/cursor/mcp-setup.md](../platform-adapters/cursor/mcp-setup.md) 第 6 节。

### 3.4 使用方式变化

- **旧方式**：主 Agent 调用 `write_decision` 写入 `agent_decision.json`，再由 `run_skill.py` / 文件监听触发 `dynamic_agent_kill.py` 执行。
- **新方式**：主 Agent 在对话中说明「推进 change-id 的 X.X 任务」或直接调用 MCP 工具 **`run_langgraph(change_id="xxx", task_range="2.1-2.4")`**，后端从 `openspec/changes/xxx/tasks.md` 解析任务并执行；无需再写 `agent_decision.json`。
- **断点续跑**：若某次 `run_langgraph` 返回了 `thread_id` 与 `checkpoint_id`，后续可用 **`resume_langgraph(change_id, thread_id, checkpoint_id)`** 从该检查点恢复。

---

## 4. 旧配置如何处理

- **保留 agent-team**：若仍在使用旧 MCP `agent-team`（`agent_team_mcp_server.py`），可暂时保留；与 **langgraph-backend** 可并存，但推荐逐步改为仅使用 `run_langgraph` / `resume_langgraph`。
- **移除文件监听**：若扩展或脚本中有对 `agent_decision.json` 的 `fs.watch` 等监听，建议移除，避免与 MCP 双触发导致重复执行。
- **不再依赖 agent_decision.json**：新后端不读取该文件，任务列表来自 `openspec/changes/{change_id}/tasks.md`。

---

## 5. 参考文档

- LangGraph 后端说明：[langgraph_backend/README.md](./langgraph_backend/README.md)
- Cursor MCP 配置（含 langgraph-backend）：[platform-adapters/cursor/mcp-setup.md](../platform-adapters/cursor/mcp-setup.md)
- 验收与脚本：[design/documents/migrate-langgraph-backend/records/](../design/documents/migrate-langgraph-backend/records/) 下功能验收与最小验收脚本

---

**文档版本**: v1.0  
**变更**: migrate-langgraph-backend  
**对应 tasks**: 5.1–5.4
