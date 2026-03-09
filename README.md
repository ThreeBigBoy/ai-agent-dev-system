# 项目简介：多 Agent 协同开发系统（V2.2 思想）

本仓库是多 Agent 协同开发体系的基础设施仓库，用于把「主 Agent 统筹 + 子 Agent 分工 + Skill 执行 + 运行后端承接」收敛成一套可复用的工程化机制。

- 对**业务项目**而言：它提供 OpenSpec 规范、全局规则与 Skills，作为跨项目可复用的治理内核；  
- 对 **Cursor / VS Code / 第三方插件** 而言：它通过 `platform-adapters/*/` 提供宿主适配方案，而不是把某个宿主写死在规范里。

本 `README.md` 仅作为**总览与导航入口**，不作为治理规则权威源。具体规则、角色、技能和运行约束以仓库内权威文档为准。

---

## V2.2 核心思想：治理内核宿主无关，宿主入口各归其位

在 V2.1 的基础上，V2.2 进一步强调：

- **治理内核层（宿主无关）**  
  - 文件：`OpenSpec.md`、`global-rules/*.md`、`agents/*.md`、`skills/*/SKILL.md`  
  - 职责：定义变更机制、角色边界、技能触发、日志制度、审核与闭环规则。

- **宿主适配层（platform-adapters/*/）**  
  - 文件：`platform-adapters/cursor/*`、`platform-adapters/vscode/*`、`platform-adapters/generic/*`  
  - 职责：描述不同宿主如何加载规则、如何接线 MCP / 扩展、如何实现 decision_sink / runtime_trigger / feedback_bridge / workspace_binding。

- **宿主入口层（各宿主要求的位置）**  
  - 示例：  
    - Cursor：`.cursor/rules/*.mdc`  
    - VS Code：根 `AGENTS.md`、`.github/agents/*.agent.md`  
  - 职责：作为宿主可直接发现的「最薄入口壳」，不再堆叠厚制度正文。

- **运行后端层（可插拔）**  
  - 当前默认实现：`agent_team_project/`  
  - 职责：承接决策写入、执行、反馈与状态持久化；不得改写治理层角色与日志制度。

> 一句话：**OpenSpec + global-rules + agents + skills 定义「怎么办」；platform-adapters 定义「各宿主怎么接线」；运行后端只负责「按决策执行」，不改变规则。**

---

## 规则优先级

本仓库统一采用以下优先级（数值越小优先级越高）：

1. `OpenSpec.md`  
2. `global-rules/*.md`  
3. `agents/*.md`  
4. `skills/*/SKILL.md`  
5. `platform-adapters/*/*.md`  
6. 宿主入口文件（如 `.cursor/rules/*.mdc`、根 `AGENTS.md`、`.github/agents/*.agent.md` 等）  
7. 运行后端实现（如 `agent_team_project/`）

若发生冲突，一律以上位规则为准；宿主入口文件与运行后端不得提升自己为规则来源。

---

## 关键约束（与所有宿主共享）

- **迭代日志**：  
  - 项目级迭代日志采用 OpenSpec 约定的内部目录结构，记录中必须写明当前 `change-id`。  
  - 每次在某一 change-id 上下文中调用 Agent 或 Skill，都应追加一条记录。

- **记录归类**：  
  - 验收记录、评审记录、复盘、对齐结论等应放入 OpenSpec 约定的内部变更记录目录。  

- **治理层角色全集**：  
  - 主 Agent + 产品经理 Agent + 架构 Agent + 前端 Agent + 后端 Agent + 测试 Agent + 文档 Agent + Bug 修复 Agent。  
  - 角色说明见 `agents/README.md` 及各子文件。

- **运行后端**：  
  - `agent_team_project/` 是当前默认运行后端，只是实现层；  
  - 仅覆盖 5 个执行角色（产品经理、架构师、前端工程师、后端工程师、测试工程师），不改变治理层角色全集。

- **模型使用策略**：  
  - 白名单宿主（当前为 Cursor 官方、VS Code 官方 / GitHub Copilot）下，主 Agent 与子 Agent 均优先使用宿主内置模型；  
  - 第三方宿主（当前明确支持 Continue、OpenAI-Codex）下，主 Agent 优先使用宿主内置模型，但子 Agent / 运行后端直接走个人自定义 OpenAI 兼容 API 模型调度策略；  
  - 若宿主内置模型无响应、异常或不可用，再按对应 adapter / runtime 配置降级到个人自定义 OpenAI 兼容 API 模型链路；  
  - 具体到 Cursor 宿主下的当前映射与模型名单，见 `platform-adapters/cursor/*` 与 `agent_team_project/runtime_config.json`。

---

## 仓库结构概览

- `OpenSpec.md`  
  项目宪法与变更机制，定义 change-id、文档目录、变更启动顺序和基础协作规则。

- `global-rules/`  
  全局规则目录入口。  
  - `projects-rules-for-agent.md`：项目通用规则、变更入口、自检与迭代日志要求；  
  - `skills-rules-for-agent.md`：Agent 与 Skills 映射及触发约定；  
  - `readme-rules-for-agent.md`：README 编写与维护规范。

- `agents/`  
  角色治理层说明，定义主 Agent 与各子 Agent 的职责边界，以及与运行后端的关系。

- `skills/`  
  每个技能目录下的 `SKILL.md` 与 REFERENCE 约定具体执行步骤和产出物最低结构。

- `platform-adapters/`  
  宿主适配层文档：  
  - `platform-adapters/cursor/*`：Cursor 规则加载、MCP 接线、反馈桥等；  
  - `platform-adapters/vscode/*`：VS Code Agent Chat 入口与模式映射；  
  - `platform-adapters/generic/*`：第三方插件的能力检查清单与适配模板。

- `AGENTS.md`  
  根级别的多宿主 Agent 说明与规则优先级，供 VS Code 等支持根 AGENTS 的宿主加载。

- `agent_team_project/`  
  默认运行后端说明与实现（可选用），实现决策执行与反馈。

- `新用户快速开始.md`
  新用户从 Git 下载仓库后，按宿主选择初始化手册并完成首次 GUI 走查的总入口。

---

## 建议阅读顺序

1. **理解规范与变更机制**：  
   - `OpenSpec.md`
2. **理解任务执行机制与技能映射**：  
   - `global-rules/projects-rules-for-agent.md`  
   - `global-rules/skills-rules-for-agent.md`
3. **理解多 Agent 角色治理边界**：  
   - `AGENTS.md`（根）  
   - `agents/主Agent.md`  
   - `agents/README.md`
4. **如需理解默认执行链路**：  
   - `agent_team_project/README.md`  
   - `platform-adapters/cursor/*`（若在 Cursor 宿主下使用）
5. **如需快速上手某一宿主**：
   - `新用户快速开始.md`

补充说明：

- V2.1 / V2.2 的详细重构背景、内部验收记录和设计推演资料属于维护者内部资料，默认不作为新用户入口公开依赖。  
- 新用户按本 README、`AGENTS.md`、`OpenSpec.md` 与各宿主 SOP 即可完成初始化与使用。

---

## 使用方式

- **作为人类读者**：  
  - 把本文件当作仓库导航页，用于快速找到治理内核文档、宿主 adapter 文档与运行后端说明。

- **作为 AI 协作入口**：  
  - 实际身份、行为和执行约束以 `OpenSpec.md`、`global-rules/`、`agents/`、`skills/` 为准；  
  - 宿主如何加载这些规则，由对应的 `platform-adapters/*/` 与入口文件（如 `.cursor/rules/*.mdc`、根 `AGENTS.md`）决定；  
  - 本文件不直接驱动执行逻辑，只提供整体视图与导航。
