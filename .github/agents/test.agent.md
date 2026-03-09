---
description: VS Code 入口壳 - 测试 Agent
---

# Test Agent Entry

当前模式对应治理层中的 **测试 Agent**。

执行前必须遵循：

1. 优先读取并遵循：
   - `OpenSpec.md`
   - `global-rules/projects-rules-for-agent.md`
   - `global-rules/skills-rules-for-agent.md`
   - `agents/子Agent-测试.md`
2. 按 `skills-rules-for-agent.md` 触发本角色主导技能：
   - 主导：`func-test`
3. 每次执行技能前，先读取对应 `skills/*/SKILL.md`。
4. 不把当前入口文件当作治理规则权威源；若与上位文档冲突，以治理层为准。
