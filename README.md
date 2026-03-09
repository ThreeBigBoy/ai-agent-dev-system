# ai-agent-dev-system

本仓库是多 Agent 协同开发体系的基础设施仓库，用于把“主 Agent 统筹 + 子 Agent 分工 + Skill 执行 + 运行后端承接”收敛成一套可复用的工程化机制。

本 `README.md` 仅作为**总览与导航入口**，不作为治理规则权威源。具体规则、角色、技能和运行约束以仓库内权威文档为准。

## V2.1 核心思想

V2.1 的目标不是推翻既有 2.0 方案，而是做“分层归位”：

- 治理层只负责规则、角色、技能、日志和审核边界。
- 运行层只负责决策落盘、执行、反馈和状态持久化。
- 主 Agent 负责统筹、分工、审核和闭环，默认不直接执行具体技能。
- `agent_team_project/` 是默认运行后端，不是治理规则权威源。

## 权威优先级

本仓库统一采用以下优先级：

1. `OpenSpec.md`
2. `global-rules/*.md`
3. `agents/*.md`
4. `skills/*/SKILL.md`
5. `.cursor/rules/*.md`
6. `agent_team_project/`

若发生冲突，一律以上位规则为准。

## 关键约束

- 迭代日志主口径统一为项目级 `design/documents/迭代日志.md`，记录中必须写明当前 `change-id`。
- `design/documents/[change-id]/records/` 仅用于验收记录、评审记录、复盘、对齐结论等变更级记录。
- 治理层角色全集由主 Agent 与产品经理、架构、前端、后端、测试、文档、Bug 修复等子 Agent 构成。
- 默认运行后端 `agent_team_project/` 当前只覆盖 5 个执行角色：产品经理、架构师、前端工程师、后端工程师、测试工程师。

## 仓库结构

- [OpenSpec.md](/Users/billhu/Documents/AI%20OnePeace/AI%20Dev/01ProjectsDesignManage/ai-agent-dev-system/OpenSpec.md)
  项目宪法与变更机制，定义 change-id、文档目录、变更启动顺序和基础协作规则。

- [global-rules/README.md](/Users/billhu/Documents/AI%20OnePeace/AI%20Dev/01ProjectsDesignManage/ai-agent-dev-system/global-rules/README.md)
  全局规则目录入口。重点包括 `projects-rules-for-agent.md` 与 `skills-rules-for-agent.md`。

- [agents/README.md](/Users/billhu/Documents/AI%20OnePeace/AI%20Dev/01ProjectsDesignManage/ai-agent-dev-system/agents/README.md)
  角色治理层说明，定义主 Agent、子 Agent、治理层与运行层的关系。

- [agent_team_project/README.md](/Users/billhu/Documents/AI%20OnePeace/AI%20Dev/01ProjectsDesignManage/ai-agent-dev-system/agent_team_project/README.md)
  默认运行后端说明，定义执行链路、runtime config 和模型策略。

- [多Agent方案V2.1重构方案.md](/Users/billhu/Documents/AI%20OnePeace/AI%20Dev/01ProjectsDesignManage/ai-agent-dev-system/%E5%A4%9AAgent%E6%96%B9%E6%A1%88V2.1%E9%87%8D%E6%9E%84%E6%96%B9%E6%A1%88.md)
  V2.1 的完整重构背景、蓝图和落地改造清单。

## 建议阅读顺序

1. 先读 [OpenSpec.md](/Users/billhu/Documents/AI%20OnePeace/AI%20Dev/01ProjectsDesignManage/ai-agent-dev-system/OpenSpec.md)，理解变更机制和文档口径。
2. 再读 [global-rules/projects-rules-for-agent.md](/Users/billhu/Documents/AI%20OnePeace/AI%20Dev/01ProjectsDesignManage/ai-agent-dev-system/global-rules/projects-rules-for-agent.md) 与 [global-rules/skills-rules-for-agent.md](/Users/billhu/Documents/AI%20OnePeace/AI%20Dev/01ProjectsDesignManage/ai-agent-dev-system/global-rules/skills-rules-for-agent.md)，理解任务执行机制与技能映射。
3. 再读 [agents/主Agent.md](/Users/billhu/Documents/AI%20OnePeace/AI%20Dev/01ProjectsDesignManage/ai-agent-dev-system/agents/%E4%B8%BBAgent.md) 与 [agents/README.md](/Users/billhu/Documents/AI%20OnePeace/AI%20Dev/01ProjectsDesignManage/ai-agent-dev-system/agents/README.md)，理解角色治理边界。
4. 如需理解默认执行链路，再读 [agent_team_project/README.md](/Users/billhu/Documents/AI%20OnePeace/AI%20Dev/01ProjectsDesignManage/ai-agent-dev-system/agent_team_project/README.md)。
5. 如需看完整重构背景与决策过程，再读 [多Agent方案V2.1重构方案.md](/Users/billhu/Documents/AI%20OnePeace/AI%20Dev/01ProjectsDesignManage/ai-agent-dev-system/%E5%A4%9AAgent%E6%96%B9%E6%A1%88V2.1%E9%87%8D%E6%9E%84%E6%96%B9%E6%A1%88.md)。

## 使用方式

- 作为人类读者：把本文件当作仓库导航页，用于快速找到权威文档和理解 V2.1 的整体分层。
- 作为 AI 协作入口：实际身份、行为和执行约束以 `.cursor/rules/`、`OpenSpec.md`、`global-rules/`、`agents/`、`skills/` 为准，不以本文件直接驱动执行。

## 补充说明

- 多 Agent 2.0 的总指挥入口模板参考文档位于 `agents/Reference/主Agent-总指挥入口模板-参考.md`。
- 外部方案归档位于 `otherDocuments/【方案】Cursor 多Agent协同2.0(真协同）/`；仓库内版本为当前协作和维护的主入口。
