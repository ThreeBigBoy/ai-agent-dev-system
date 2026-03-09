## Cursor 运行链路集成（runtime-integration）

本文件说明 ai-agent-dev-system 在 Cursor 宿主下，如何将「主 Agent 决策」与运行后端（如 `agent_team_project/`）串联起来，形成完整运行链路。

### 1. 抽象接口

在 V2.2 中，运行链路被抽象为四类宿主无关接口：

1. **`decision_sink`**  
   - 用途：接收主 Agent 的结构化决策对象。  
   - Cursor 当前实现：通过 MCP server `agent-team` 暴露的工具（如 `write_decision`），写入运行后端约定的决策文件（优先 `agent_decision.json`，并兼容旧名 `cursor_decision.json`）。

2. **`runtime_trigger`**  
   - 用途：触发运行后端开始执行。  
   - Cursor 当前实现：用户使用快捷键或命令面板触发自定义扩展，由扩展启动/唤起运行后端进程（或向其发送执行指令）。

3. **`feedback_bridge`**  
   - 用途：把运行结果送回 Chat。  
   - Cursor 当前实现：见 `platform-adapters/cursor/feedback-bridge.md`（反馈文件 + 剪贴板 + 人工粘贴的降级方案）。

4. **`workspace_binding`**  
   - 用途：告诉运行后端当前宿主下应绑定到哪个运行目录或工作目录。  
   - Cursor 当前实现：通过 MCP 环境变量 `AGENT_TEAM_PROJECT_ROOT`（见 `mcp-setup.md`），绑定到 `ai-agent-dev-system/agent_team_project`。

5. **`model_provider_policy`**  
   - 用途：说明当前宿主下主 Agent / 子 Agent 与运行后端优先使用哪类模型提供方。  
   - Cursor 当前实现：优先使用宿主内置模型；若内置模型无响应、异常或不可用，再降级到个人自定义 OpenAI 兼容 API 模型链路。具体候选模型见 `agent_team_project/runtime_config.json`。

### 2. 典型执行流程（示意）

1. 用户在 Cursor Chat 中与主 Agent 讨论需求/变更。  
2. 主 Agent 按 OpenSpec + global-rules + agents/skills 约定拆解任务，并在需要时调用 MCP 工具：  
   - 将本次变更的结构化决策写入 `decision_sink`（如 `agent_decision.json`）。  
3. 用户通过快捷键或命令面板触发运行后端（`runtime_trigger`）：  
   - 运行后端读取 `AGENT_TEAM_PROJECT_ROOT`，定位 Cursor 当前约定的运行目录；  
   - 从 `decision_sink` 中读取最新决策，按其中说明修改文件、跑命令等。  
4. 运行后端执行完成后，将结果写入反馈文件（优先 `agent_feedback.txt`，并兼容旧名 `cursor_feedback.txt`，作为 `feedback_bridge` 的输入）。  
5. Cursor 自定义扩展监听反馈文件并复制内容到剪贴板，提醒用户粘贴回 Chat。  
6. 用户粘贴反馈后，主 Agent 根据反馈决定：  
   - 是否需要进一步拆解与执行；  
   - 是否需要更新文档或迭代日志；  
   - 是否可以宣告本次任务闭环。

### 3. 与治理内核的关系

- 整条运行链路只是一种「如何执行决策」的实现；  
- 不改变以下治理优先级与规则：
  1. `OpenSpec.md`  
  2. `global-rules/*.md`  
  3. `agents/*.md`  
  4. `skills/*/SKILL.md`  
  5. `platform-adapters/*/*.md`  
  6. 宿主入口文件（如 `.cursor/rules/*.mdc`、根 `AGENTS.md` 等）  
  7. 运行后端实现（如 `agent_team_project/`）

如果未来在 Cursor 中采用 Subagent、Serverless 函数或其他执行链路，只需在本 adapter 层更新 `decision_sink` / `runtime_trigger` / `feedback_bridge` / `workspace_binding` 的实现，无需修改治理内核文档。
