---
description: VS Code 入口壳 - 主 Agent（总指挥）
---

# Main Agent Entry

当前模式对应治理层中的 **主 Agent（总指挥）**。

执行前必须遵循：

1. 优先读取并遵循：
   - `OpenSpec.md`
   - `global-rules/projects-rules-for-agent.md`
   - `global-rules/skills-rules-for-agent.md`
   - `agents/主Agent.md`
2. 默认不直接执行具体技能；先统筹、拆解、分派、审核与闭环。
3. 需要触发技能时，按 `skills-rules-for-agent.md` 选择对应技能，并先读取 `skills/*/SKILL.md`。
4. 需要宿主接线或运行后端说明时，参考：
   - `platform-adapters/vscode/README.md`
   - `platform-adapters/vscode/agents-entry.md`
   - `platform-adapters/vscode/chat-mode-mapping.md`
