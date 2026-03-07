# agents 说明

本目录存放 **主 Agent** 与治理层各子 Agent 的角色定义（权责、技能、配额、产出路径等），与 `ai-agent-dev-system/global-rules/`、`skills-rules-for-agent.md`、各技能 SKILL 配套使用，作为「谁来做、按什么规范做」的**治理层权威来源**。

---

## 一、治理层角色全集

本仓库的治理层角色全集固定为：

- 主 Agent
- 产品经理 Agent
- 架构 Agent
- 前端 Agent
- 后端 Agent
- 测试 Agent
- 文档 Agent
- Bug 修复 Agent

说明：

- 主 Agent 负责统筹、决策、审核与闭环，不进入默认 backend 的 executor 枚举。
- 文档 Agent、Bug 修复 Agent 属于治理层合法角色，但默认不进入 `agent_team_project` 的 executor 子集。

---

## 二、治理层与运行层的关系

- **治理层**：由 `agents/`、`OpenSpec.md`、`global-rules/*.md`、`skills-rules-for-agent.md` 组成，负责定义角色边界、技能映射、日志要求、质量审核与配额策略。
- **运行层**：负责“决策落盘 -> 执行 -> 反馈 -> 状态持久化”的具体实现。默认运行后端为 `ai-agent-dev-system/agent_team_project/`。
- **边界**：运行层不是角色定义权威源；运行层只能承接执行，不能改写治理层角色边界。

---

## 三、默认 backend 的 executor 子集

默认 backend：`ai-agent-dev-system/agent_team_project/`

该 backend 当前固定支持以下 5 个 executor：

- 产品经理
- 架构师
- 前端工程师
- 后端工程师
- 测试工程师

与治理层角色全集的关系：

- 这是**运行层执行子集**，不是治理层角色全集。
- 它对应治理层中的：产品经理 Agent、架构 Agent、前端 Agent、后端 Agent、测试 Agent。
- 它**不覆盖**：主 Agent、文档 Agent、Bug 修复 Agent。

---

## 四、与 Cursor Settings 里 Subagent 的区别

### 本目录：agents 下的 .md 文件

- **本质**：仓库内的角色说明文档，AI 通过 Rules/提示「先读 xxx.md」在对话中扮演该角色。
- **加载方式**：由 `.cursor/rules` 或用户指令触发「读取 主Agent.md / 子Agent-xxx.md」后，当前会话按该文档行为。
- **并行与隔离**：无真正并行；同一会话顺序扮演不同角色，或用户手动切上下文。
- **模型/工具**：默认不区分；配额与模型边界由治理层规则约束。
- **版本与复用**：在 Git 中版本化，可跨项目复用、与 OpenSpec/skills 一起演进。
- **适用场景**：定义角色、职责、审核关系和规范边界。

### Cursor 产品功能：Settings → Subagent

- **本质**：Cursor 内置的独立 Agent 实例，可单独配置提示、工具、模型，支持并行执行。
- **定位**：执行入口或运行载体，不是角色规范的权威源。
- **适用场景**：需要真实并行（多路研究/多路编码）或按角色分模型/分工具时，作为运行实现。

---

## 五、推荐用法

- **agents = 唯一权威的角色定义**  
  所有「角色名、权责边界、主导/联动技能、配额、产出路径、审核与改进」以本目录的 .md 与 `global-rules/`、`skills-rules` 为准；新增/修改角色只改这一套，避免多处维护。

- **主会话以「主 Agent」身份运行**  
  通过 `.cursor/rules/agent.mdc` 约定先读 `主Agent.md`，由主 Agent 做任务拆解、审核、进度与闭环。

- **运行层可以有多种实现**  
  - 方式 A：同一会话按需读取 `子Agent-xxx.md` 串行执行。
  - 方式 B：通过 Cursor Subagent 做并行执行。
  - 方式 C：通过 `agent_team_project` 这类 backend 承接默认执行链路。

- **无论使用哪种运行层实现**  
  角色边界、技能映射、日志口径与审核要求仍以 `agents + OpenSpec + global-rules + skills-rules` 为准。

---

## 六、小结

| 目标 | 建议 |
|------|------|
| **治理权威唯一** | 以 **agents + global-rules + OpenSpec + skills-rules** 作为唯一治理来源。 |
| **角色全集清晰** | 治理层固定为主 Agent 与以下子 Agent：产品经理、架构、前端、后端、测试、文档、Bug 修复。 |
| **运行层边界清晰** | `agent_team_project` 只是默认 backend，其 5 个 executor 只是治理层角色全集的子集。 |
| **可维护与复用** | 角色与流程的增删改只做在 **agents / global-rules / OpenSpec**，运行层按需替换。 |
