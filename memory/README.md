## `memory/`：长期记忆库

本目录用于存放从多次任务复盘、故障修复与成功实践中提炼出的**长期记忆**，通过结构化元数据（frontmatter）标记适用范围，指导后续类似任务的决策与执行。

### 定位

- 与 `design/documents/[change-id]/records/` 下的一次性复盘/验收记录区分：
  - **records/**：针对单个 change-id 的具体记录；
  - **memory/**：跨 change-id / 跨项目具有长期复用价值的模式和经验。
- 记忆条目用于：
  - 复用已验证的最佳实践（patterns）；
  - 显式标注常见陷阱与反模式（anti-patterns）；
  - 记录项目/用户的偏好（preferences，需用户确认）；
  - 描述复杂场景的 SOP（playbooks）；
  - 汇总跨项目的深度反思（reflections）。

### 目录结构

```text
memory/
├── README.md          # 本说明文档
├── schema.md          # frontmatter 规范与示例
├── patterns/          # 【模式】可复用的成功实践
├── anti-patterns/     # 【反模式】常见坑点与反例
├── preferences/       # 【偏好】项目/用户的偏好（需确认）
├── playbooks/         # 【剧本】复杂场景的标准操作流程
└── reflections/       # 【反思】跨项目的经验总结
```

### 使用建议（简要）

- 在启动新任务或变更分析前，主 Agent 或相关子 Agent 应根据当前项目、宿主与任务类型检索匹配的记忆条目，并将其作为方案设计与执行的参考；
- 记忆条目应在复盘阶段由主 Agent 明确判断与创建，避免自动化记录导致噪音和误导；
- 具体 frontmatter 字段与沉淀流程见 `schema.md`。

