## VS Code Chat 模式映射（chat-mode-mapping）

本文件用于说明：在 VS Code 下，不同的 Agent / Chat 模式如何与本仓库中的 **主 Agent与子 Agent 角色** 对应。

### 1. 角色映射建议

可按以下方式将 VS Code 中的 Agent 模式与本仓库角色对齐（名称仅为示例）：

- `Main Coordinator` → `agents/主Agent.md`（主 Agent，总指挥）；  
- `Product` → `agents/子Agent-产品经理.md`；  
- `Architect` → `agents/子Agent-架构.md`；  
- `Frontend` → `agents/子Agent-前端.md`；  
- `Backend` → `agents/子Agent-后端.md`；  
- `Tester` → `agents/子Agent-测试.md`；  
- `Docs` → `agents/子Agent-文档.md`；  
- `BugFix` → `agents/子Agent-Bug修复.md`。

### 2. 映射时应遵循的约定

对每个 VS Code Agent 模式，应在其入口说明中约定：

1. **自我定位**：明确自己是主 Agent 还是哪个子 Agent；  
2. **遵循文档**：在执行任务前，先阅读并遵循：  
   - `OpenSpec.md`；  
   - `global-rules/projects-rules-for-agent.md`；  
   - `global-rules/skills-rules-for-agent.md`；  
   - 对应的 `agents/*.md`。  
3. **技能触发**：  
   - 按 `skills-rules-for-agent.md` 为本角色选择主导/联动技能；  
   - 每次执行某个 Skill 前先读取对应 `skills/*/SKILL.md`，再按其中步骤执行。

### 3. 与运行后端的关系

- VS Code Agent 的职责是理解与执行治理规则，不必直接知道运行后端的全部细节；  
- 若需要通过 MCP 或其他机制触发运行后端，应在 VS Code 插件层实现 `decision_sink` / `runtime_trigger` / `feedback_bridge` / `workspace_binding`，并在本目录或相关文档中说明；  
- 无论是否有运行后端，Agent 都应遵守 OpenSpec 与 global-rules 的变更与迭代日志约定。

