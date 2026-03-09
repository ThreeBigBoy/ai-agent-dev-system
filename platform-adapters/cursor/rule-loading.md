## Cursor 规则加载（rule-loading）

本文件说明 **Cursor IDE 如何加载 ai-agent-dev-system 的治理规则**，以及 `.cursor/rules/*.mdc` 在 V2.2 方案中的定位。

### 1. 定位

- `.cursor/rules/*.mdc` 属于 **宿主入口层**：  
  - 必须放在 Cursor 工作区根目录的 `.cursor/rules/` 下，才能被 Cursor 自动发现；  
  - 内容应尽量「变薄」，只承担**入口壳与跳转**职责。
- 真正的治理规则权威源是：
  - `OpenSpec.md`  
  - `global-rules/*.md`  
  - `agents/*.md`  
  - `skills/*/SKILL.md`

### 2. 推荐文件

在使用本仓库作为 Cursor 规则来源时，推荐在工作区（或多根工作区的第一个根）下存在：

- `.cursor/rules/agent.mdc`  
  - 只负责声明「当前对话身份为主 Agent，总指挥」，并指向 `agents/主Agent.md` 与 `global-rules/*`。  
- `.cursor/rules/global-rules.mdc`  
  - 只负责声明「对话开始时需先读取 `projects-rules-for-agent.md` 与 `skills-rules-for-agent.md`」。

两者都不再内嵌大段制度正文，而是把厚内容统一留在治理内核层。

### 3. 工作区推荐用法（多根场景）

1. 使用 Cursor 打开多根工作区，并确保 **ai-agent-dev-system** 是第一个根目录（因为 Cursor 只会从第一个根加载 `.cursor/rules/`）。  
2. 在 `ai-agent-dev-system/.cursor/rules/` 下放置上述精简版 `agent.mdc` 与 `global-rules.mdc`。  
3. 如有其他业务项目仓库，可在那些仓库中只维护 `openspec/` 与项目内文档，由 ai-agent-dev-system 统一提供治理规范与技能。

### 4. 行为预期

当 Cursor 在该工作区内打开对话时：

1. 首先加载 `.cursor/rules/*.mdc`，识别本会话为「主 Agent 总指挥」，并获知需要优先读取哪些治理规则文件。  
2. 按 `global-rules/` 与 `agents/` 的约定，确定当前任务的执行方 Agent 与应触发的 Skill，先读取对应 `SKILL.md` 再执行。  
3. Cursor 本身不参与治理决策，只负责按 `.mdc` 指示，让当前模型/会话遵守上述规则。

更多关于 Cursor MCP 与运行后端接线，见本目录下的 `mcp-setup.md` 与 `runtime-integration.md`。

