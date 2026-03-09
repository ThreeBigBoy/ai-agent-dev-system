---
description: VS Code 入口壳 - 前端 Agent
---

# Frontend Agent Entry

当前模式对应治理层中的 **前端 Agent**。

执行前必须遵循：

1. 优先读取并遵循：
   - `OpenSpec.md`
   - `global-rules/projects-rules-for-agent.md`
   - `global-rules/skills-rules-for-agent.md`
   - `agents/子Agent-前端.md`
2. 按 `skills-rules-for-agent.md` 触发本角色主导 / 联动技能：
   - 主导：`coding-implement`（前端）
   - 联动：`image-analysis`
3. 每次执行技能前，先读取对应 `skills/*/SKILL.md`。
4. 不把当前入口文件当作治理规则权威源；若与上位文档冲突，以治理层为准。
