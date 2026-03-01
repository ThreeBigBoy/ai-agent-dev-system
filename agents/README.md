# agents 说明

本目录存放 **主 Agent** 与 **7 个子 Agent** 的角色定义（权责、技能、配额、产出路径等），与 `ai-agent-dev-system/global-rules/`、`skills-rules-for-agent.md`、各技能 SKILL 配套使用，作为「谁来做、按什么规范做」的**规范侧权威来源**。

---

## 与 Cursor Settings 里 Subagent 的区别（效率与质量视角）

### 本目录：agents 下的 .md 文件

- **本质**：仓库内的角色说明文档，AI 通过 Rules/提示「先读 xxx.md」在对话中扮演该角色。
- **加载方式**：由 `.cursor/rules` 或用户指令触发「读取 主Agent.md / 子Agent-xxx.md」后，当前会话按该文档行为。
- **并行与隔离**：无真正并行；同一会话顺序扮演不同角色，或用户手动切上下文。
- **模型/工具**：不区分；所有角色共用当前会话的模型与工具，配额在提示语里约束（如禁止 Opus）。
- **版本与复用**：在 Git 中版本化，可跨项目复用、与 OpenSpec/skills 一起演进，评审、协作清晰。
- **与规范联动**：与 skills-rules、projects-rules、SKILL.md、OpenSpec 强绑定，权责、技能、产出路径、审核改进均写在一处。
- **适用场景**：定义「角色是谁、负责什么、按什么规范做、产出写哪」；主 Agent 拆任务、审核、闭环。

### Cursor 产品功能：Settings → Subagent

- **本质**：Cursor 内置的独立 Agent 实例，可单独配置提示、工具、模型，支持并行执行。
- **加载方式**：由 Cursor 在任务拆解时拉起，每个 Subagent 有独立上下文与执行环境。
- **并行与隔离**：有；多个 Subagent 可同时跑（如一个查文档、一个写代码），互不干扰。
- **模型/工具**：可区分；每个 Subagent 可配不同模型、不同工具权限，便于重任务用强模型、轻任务用轻量模型。
- **版本与复用**：配置在 Cursor 应用/账号侧，不随仓库走，难以多项目共享、不易做 Code Review。
- **与规范联动**：若单独写一套提示，易与 agents / global-rules 脱节，出现两套定义不一致。
- **适用场景**：需要真实并行（多路研究/多路编码）或按角色用不同模型/工具时，作为执行载体。

---

## 推荐用法：两者配合，结果最优

- **agents = 唯一权威的角色定义**  
  所有「角色名、权责边界、主导/联动技能、配额、产出路径、审核与改进」以本目录的 .md 与 `global-rules/`、`skills-rules` 为准；新增/修改角色只改这一套，避免多处维护。

- **主会话仍以「主 Agent」身份运行**  
  通过 `.cursor/rules/agent.mdc` 约定先读 `主Agent.md`，由主 Agent 做任务拆解、审核、进度与闭环；子 Agent 的「执行」可以是：
  - **方式 A（仅文档）**：同一会话按任务类型读取对应 `子Agent-xxx.md` 后按该角色执行（无并行、无分模型）。
  - **方式 B（配合 Subagent）**：主 Agent 拆出可并行的子任务后，由 Cursor 拉起 Subagent；**Subagent 的 System Prompt 里只写简短身份 + 指向本目录**，例如：
    - 「你是前端 Agent。执行前请先读取 `ai-agent-dev-system/agents/子Agent-前端.md` 与 `skills-rules-for-agent.md` 中本角色技能，再按其中约定与对应 SKILL 执行。」
    - 这样 Subagent 的**行为仍由 agents 与 skills 决定**，Settings 里只做「身份入口 + 可选模型/工具」，不重复写一整份角色说明。

- **何时用 Subagent 更合适**  
  - 需要**并行**（例如同时做需求分析 + 工程结构分析，或同时多模块编码）时，用 Subagent 并行跑，每个的 Prompt 指向对应 `子Agent-xxx.md`。  
  - 需要**按角色用不同模型**（例如测试 Agent 仅慢速、架构 Agent 可 Opus）时，在 Subagent 配置里为该实例选对应模型，提示里仍只写「先读 子Agent-xxx.md 与 skills-rules」。  
  - 单线串行、且不强调分模型时，仅用 agents + 主 Agent 拆任务 + 同一会话按需读 子Agent-xxx.md 即可，简单且与规范一致。

- **避免的用法**  
  - 不在 Settings Subagent 里再写一套与 agents 平行的长角色说明（易漂移、难维护）。  
  - 不把「角色定义」拆成两半（一半在 .md、一半在 Settings）；要么全在 .md，要么 Settings 里只做「身份 + 读 xxx.md」的短提示。

---

## 小结

| 目标 | 建议 |
|------|------|
| **质量与一致性** | 以 **agents + global-rules + skills-rules** 为唯一角色与规范来源；Subagent 仅作执行入口，提示中「先读 xxx.md」。 |
| **效率（并行/分模型）** | 需要时用 **Cursor Subagent** 做并行或分模型，每个 Subagent 的 Prompt 简短引用本目录与 skills-rules，不重复写长说明。 |
| **可维护与复用** | 角色与流程的增删改只做在 **agents / global-rules**，便于版本化、评审和多项目复用；Settings 只做「谁在什么时机被拉起、用啥模型」。 |

这样既能保证行为统一、可追溯（规范侧全在仓库），又能在需要时用 Cursor 的并行与分模型能力提升效率。
