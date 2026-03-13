# sys-rules-memory-refactor-v2-4

本 change-id 用于跟踪 `global-rules/projects-rules-for-agent.md` 在 V2.4/V2.4.1 下的瘦身与 memory 化改造，包括：

- 在 rules 中保留 MUST 级核心条款，将经验性/示例性内容迁移到 `memory/`；
- 调整 `.cursor/rules/*.mdc` 与 `agents/主Agent.md` 的 simple/heavy 加载策略；
- 为任务复杂度判定、迭代日志、模型分层与 runtime-logs × memory 协作补充对应的 memory 条目。

