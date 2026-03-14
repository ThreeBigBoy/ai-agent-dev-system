## platform-adapters 概览

`platform-adapters/` 是 **宿主适配层**，用于描述「不同 IDE / 插件 / Agent 平台如何接入 ai-agent-dev-system 的治理内核」。

- **治理内核层**（宿主无关）  
  - 文件：`OpenSpec.md`、`global-rules/*.md`、`agents/*.md`、`skills/*/SKILL.md`  
  - 职责：定义变更机制、角色边界、技能触发、日志制度、审核与闭环规则。

- **宿主适配层**（本目录）  
  - 目录：`platform-adapters/cursor/`、`platform-adapters/vscode/`、`platform-adapters/generic/`  
  - 职责：解释不同宿主如何加载入口规则、如何注入角色、如何触发运行链路、如何把运行结果送回 Chat。

- **宿主入口层**（保留在宿主要求的位置）  
  - 典型示例：  
    - Cursor：`.cursor/rules/*.mdc`  
    - VS Code：根 `AGENTS.md`、`.github/agents/*.agent.md`  
  - 职责：作为宿主可直接发现的「最薄入口壳」，不再堆叠厚制度正文。

- **运行后端层**  
  - 当前默认实现：`agent_team_project/`  
  - 职责：承接决策写入、执行、反馈与状态持久化；不得改写治理层规则。

### 当前适配状态

- `cursor/`：首个完整落地的宿主 adapter（通过 MCP + 自定义插件形成 decision_sink / runtime_trigger / feedback_bridge）。  
- `vscode/`：面向 VS Code 官方 Agent Chat 的适配层，已补充根 `AGENTS.md` 与 `.github/agents/*.agent.md` 入口骨架。  
- `generic/`：面向第三方 Codex / Agent 插件的适配层，当前明确收敛的目标宿主为 `Continue` 与 `OpenAI-Codex`。

> **运行后端触发行为的全局约定**：  
> 所有宿主在设计 `runtime_trigger`（如何根据用户指令触发运行后端）行为时，应优先遵循根仓库 `AGENTS.md` 中关于「基于 change-id 的智能触发运行后端」的结论级规则；各宿主 adapter 只需在自身文档中给出引用与少量宿主特有示例，无需重复定义触发条件，以保证多宿主行为一致性。

### 宿主模型策略摘要

- **白名单宿主**：`cursor`、`vscode`
  - 主 Agent 与子 Agent 均优先使用宿主内置模型
- **第三方宿主**：`continue`、`openai-codex`
  - 主 Agent 优先使用宿主内置模型
  - 子 Agent / 运行后端执行链路直接走个人自定义 OpenAI 兼容 API 模型调度策略

后续新增宿主，只需在本目录下新增子目录并实现对应文档与接线方案，无需修改治理内核。
