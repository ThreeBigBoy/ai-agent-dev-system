## 新宿主 adapter 编写模板（adapter-template）

本文件可作为为任意新宿主编写 adapter 文档的起点，请复制后按实际产品名称替换占位符。

注意：当前 V2.2 已明确优先支持的第三方宿主是 `Continue` 与 `OpenAI-Codex`。若为其他宿主新增 adapter，建议先参考这两个宿主的适配文档，再复制本模板。

---

## {HOST_NAME} adapter 概览

`platform-adapters/{HOST_KEY}/` 描述 ai-agent-dev-system 在 **{HOST_NAME} 宿主** 下的适配方式。

- 治理内核层：`OpenSpec.md`、`global-rules/*.md`、`agents/*.md`、`skills/*/SKILL.md`（宿主无关）；  
- 宿主适配层：`platform-adapters/{HOST_KEY}/*.md`（本目录）；  
- 宿主入口层：{HOST_NAME} 要求的入口文件或配置；  
- 运行后端层：如 `agent_team_project/` 或其他实现。

### 1. 宿主能力映射

请在此描述 {HOST_NAME} 与四个抽象接口的对应关系：

- `decision_sink`（决策写入）：  
  - 例如：通过 {HOST_NAME} 提供的配置 / 扩展，将决策写入某个 JSON 文件或服务。
- `runtime_trigger`（触发执行）：  
  - 例如：通过命令、按钮或任务机制触发运行后端脚本。
- `feedback_bridge`（反馈桥接）：  
  - 例如：通过 API / 剪贴板 / 输出面板将反馈送回 {HOST_NAME} 的 Agent 对话。
- `workspace_binding`（工作区绑定）：  
  - 例如：使用 {HOST_NAME} 的「当前工作区路径」作为运行后端的根目录。

### 2. 入口文件与配置

- 说明 {HOST_NAME} 下用于承载 rules / instructions 的入口位置与文件格式；  
- 描述如何在这些入口中引用本仓库的治理内核：  
  - `OpenSpec.md`  
  - `global-rules/projects-rules-for-agent.md`  
  - `global-rules/skills-rules-for-agent.md`  
  - `agents/*.md` 与 `skills/*/SKILL.md`。

### 3. 使用流程示例

给出一条典型使用路径，例如：

1. 用户在 {HOST_NAME} 中打开包含 ai-agent-dev-system 的工作区；  
2. 选择某个 Agent 模式（如主 Agent / 前端 Agent）；  
3. 发起新需求或变更；  
4. Agent 按 OpenSpec + global-rules 执行 request-analysis / project-analysis / coding-implement 等技能；  
5. 决策通过 `decision_sink` 写入，运行后端被 `runtime_trigger` 唤起；  
6. 运行结果通过 `feedback_bridge` 回到对话中，继续由主 Agent 协调。

### 4. 限制与降级方案

- 列出 {HOST_NAME} 当前不具备的能力（例如：无法直接向 Chat 注入消息）；  
- 说明为此采用的降级处理方式（例如：剪贴板 + 人工粘贴）；  
- 标记这些限制为宿主层约束，而非治理内核要求。
