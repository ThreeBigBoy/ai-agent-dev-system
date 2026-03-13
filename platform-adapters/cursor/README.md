## Cursor adapter 概览

`platform-adapters/cursor/` 描述 **ai-agent-dev-system 在 Cursor IDE 宿主下的适配方式**，包括：

- 如何让 Cursor 加载治理内核规则；
- 如何通过 MCP 建立 `decision_sink`（决策落盘）；
- 如何触发运行后端（`runtime_trigger`）；
- 如何把运行结果送回 Chat（`feedback_bridge`）；
- 如何在工作区与运行后端之间建立绑定（`workspace_binding`）。

### 目录结构

- `rule-loading.md`：说明 Cursor 如何通过 `.cursor/rules/*.mdc` 加载本仓库的治理规则。  
- `mcp-setup.md`：说明如何在 `~/.cursor/mcp.json` 中注册 `agent-team` MCP server。  
- `feedback-bridge.md`：说明当前基于「反馈文件 + 剪贴板」的降级反馈桥实现。  
- `runtime-integration.md`：说明 Cursor Chat 与运行后端（`agent_team_project/` 等）的集成方式。  
- `mcp.template.json`：`~/.cursor/mcp.json` 的示例模板（不会直接被 Cursor 读取）。  
- `extension/README.md`：Cursor 自定义扩展（如反馈桥插件）的补充说明。
- `从0开始初始化配置SOP与GUI走查清单.md`：新用户从 Git 下载仓库后，在 Cursor 中完成初始化配置与人工走查的操作手册。

> 注意：Cursor 相关说明都是 **adapter 文档**，不改变 OpenSpec 与 `global-rules` / `agents` / `skills` 等治理内核的优先级。

## 当前 Cursor adapter 的两项关键约束

1. **运行目录绑定**
   - Cursor 当前实现要求在 `~/.cursor/mcp.json` 中注册 `agent-team` MCP 服务，并将 `AGENT_TEAM_PROJECT_ROOT` 绑定到 `ai-agent-dev-system/agent_team_project`。  
   - 这是当前 Cursor IDE 下的实际运行约束，不要求其他宿主复用同一路径语义；VS Code 与第三方插件应优先遵循各自官方文档与 adapter 设计。
   - 建议同时设置 `AGENT_HOST_TYPE=cursor`，让运行后端识别当前属于白名单宿主。

2. **模型调用策略**
   - 主 Agent 与子 Agent 优先使用 Cursor 宿主内置模型。  
   - 若宿主内置模型无响应、异常或不可用，再降级到个人自定义 OpenAI 兼容 API 模型链路。  
   - 由于 Cursor 属于白名单宿主，运行后端中的子 Agent 维持“宿主内置模型优先”的策略。  
   - 当前默认运行后端的 API 模型配置见 `agent_team_project/runtime_config.json`；当前示例提供方为 SiliconFlow，Base URL 为 `https://api.siliconflow.cn/v1`。  
   - 推荐分工：
     - 高频轻量任务优先 `Qwen/Qwen3-8B`
     - 核心开发任务优先 `Pro/deepseek-ai/DeepSeek-V3.2`
     - 特殊复杂场景再提升到 `Pro/MiniMaxAI/MiniMax-M2.5`
     - `Pro/moonshotai/Kimi-K2.5` 作为补充可用模型保留

## 默认加载顺序规范（V2.4.2）

在 Cursor 宿主下，主 Agent 与子 Agent 应遵循以下「rules → SKILL/memory」渐进式加载顺序：

1. **simple 任务（轻量场景）**  
   - 首轮仅依赖：`.cursor/rules/*.mdc` 中的入口规则 + 当前会话上下文；  
   - 必要时按主题少量加载 `memory/` 条目（如与 runtime-logs、iteration-log 相关的 pattern/reflection）；  
   - 不强制一次性读取完整 `global-rules/projects-rules-for-agent.md` 与 `global-rules/skills-rules-for-agent.md`。

2. **heavy 任务（重规则场景）**  
   - 当 simple/heavy 判定为 heavy 时，必须追加加载：  
     - `global-rules/projects-rules-for-agent.md`（至少包含总则与当前任务相关章节）；  
     - `global-rules/skills-rules-for-agent.md` 中的 Agents ↔ Skills 映射表；  
     - 当前执行方对应的 `agents/*.md`。  
   - 在需要具体 HOW 时，再根据 `skills-rules-for-agent.md` 指定的技能与当前 change-id/主题，**按需**加载少量 `skills/*/SKILL.md` 与 `memory/*` 条目，而不是一次性读完全部记忆。

> 说明：本节仅约束加载顺序与职责分工；具体哪些章节或 memory 条目需要加载，仍以 `projects-rules-for-agent.md`、`skills-rules-for-agent.md` 与各 SKILL/memory pattern 为准。
