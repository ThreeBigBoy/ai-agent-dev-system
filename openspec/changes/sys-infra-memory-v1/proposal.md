## `sys-infra-memory-v1` 变更提案：运行日志与长期记忆体系落地（V2.3）

### Why

`ai-agent-dev-system` 需要一套与 OpenSpec / 全局规则协同的「运行日志 + 长期记忆」基础设施，用于：

- 记录多宿主、多模型下的运行技术指标（token、耗时、状态），支撑成本与健康度分析；
- 将跨 change-id、多项目反复出现的经验沉淀为长期记忆（patterns / anti-patterns / preferences 等），指导后续任务决策；
- 明确运行日志与 `design/documents/迭代日志.md` 的边界：前者聚焦技术指标，后者记录业务过程与 Agent/技能调用。

### What Changes

- 在仓库根目录新增 `runtime-logs/` 目录，用于存放运行日志相关文件：
  - `runtime-logs/model-calls/*.jsonl`：模型调用明细（JSON Lines），记录 change_id / agent_role / skill 等关键字段及 token、耗时、状态；
  - `runtime-logs/system-events/events.log`：系统事件文本日志（任务开始/结束、降级重试等）；
  - `runtime-logs/adapters/*.md`：各宿主（Cursor / VSCode / 第三方）如何采集并写入运行日志的适配说明；
  - `runtime-logs/.gitignore`：忽略 `.jsonl` / `.log` 等运行期产物，仅保留说明文档。
- 在仓库根目录新增 `memory/` 记忆库目录：
  - 约定每个记忆文件使用 YAML frontmatter 标记 `id`、`title`、`type`、`tags`、`applicable_projects`、`host_scope`、`source_change_ids` 等元数据；
  - 按 `patterns/`、`anti-patterns/`、`preferences/`、`playbooks/`、`reflections/` 分类存放记忆；
  - 提供 `README.md` 与 `schema.md` 说明使用方式与 frontmatter 规范。
- 在 `design/documents/sys-infra-memory-v1/` 中补充变更背景与实施说明文档（本 README 与后续 records）。

### Impact

- **对现有文档体系**：
  - 与 `design/documents/迭代日志.md` 形成互补：运行日志只存技术指标，不重复记录业务过程；
  - 与 `global-rules/projects-rules-for-agent.md` 中的运行日志与记忆相关约定对齐（已在 V2.3 中补充说明）。
- **对多宿主适配**：
  - 为 `platform-adapters/<host>/` 提供统一的目标目录与数据 schema 约定；
  - 后续可在各宿主 adapter 文档中补充采集实现，不影响规范本身。
- **对安全与隐私**：
  - 明确禁止在运行日志与记忆中存放完整 Prompt/回复、业务敏感数据与密钥，仅允许脱敏后的摘要与统计指标；
  - 运行日志与记忆默认本地落盘，通过 `.gitignore` 避免运行期产物进入版本控制。

### Non-Goals

- 本变更不直接引入任何外部存储或集中化日志/监控平台，仅定义本地文件结构与规范；
- 不在本阶段实现自动聚合报表或可视化，仅为后续脚本/工具预留目录与 schema。

### Dependencies

- 依赖 OpenSpec 规范文档 `ai-agent-dev-system/OpenSpec.md`（尤其是第 5、6 节）以及全局规则：
  - `global-rules/projects-rules-for-agent.md`
  - `global-rules/skills-rules-for-agent.md`
- 依赖方案文档：
  - `otherDocuments/【方案】Cursor 多Agent协同2.0(真协同)/V2.3/runtime-logging-and-agent-memory-integrated.md`

### Risks

- 若运行日志 schema 设计不合理，后续适配脚本与聚合分析的复杂度会增加；
- 如未严格遵守隐私约束，运行日志与记忆有潜在泄露敏感信息的风险。

### 协同与技能（参考）

- 本变更主要由**主 Agent**统筹，属系统基础设施级改造；
- 涉及文档与规范编写时，可视为由**文档 Agent**执行（无专属技能，参考 request-analysis / project-analysis 思路）；
- 未来若将采集脚本与 OpenSpec CLI 深度集成，可在对应变更中引入 coding-implement / project-analysis 等技能。

