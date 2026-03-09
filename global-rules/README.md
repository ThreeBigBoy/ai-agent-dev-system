# global-rules 目录说明（宿主无关）

`ai-agent-dev-system/global-rules/` 下存放的是 **可被多个项目、多种宿主复用的全局规则文档**。  
这些规则与具体 IDE / 插件无关，任何宿主只要能读取本目录的 Markdown 文件，就可以据此约束多 Agent 的行为。

本目录下除本 README 外的所有 `.md` 都应被视为**治理内核的一部分**，而非某个宿主的专用扩展文档。

---

## 目录内主要规则文件

| 文件 | 定位 |
|------|------|
| `projects-rules-for-agent.md` | 项目通用规则：任务执行机制、变更入口、代码/安全/配额/行为规范、迭代日志要求等 |
| `skills-rules-for-agent.md` | Agents 与 Skills 的赋能关系：各角色主导/联动技能、技能触发约定、产出与日志要求 |
| `readme-rules-for-agent.md` | README 与文档编写规范：结构、层级、命名与维护约定 |

> 使用本仓库时，应假设以上文件**在所有宿主下都有效**；若某宿主暂时无法自动加载这些文件，可以通过人工复制、宿主侧配置或脚本接线来补足。

---

## 不同宿主下如何加载 global-rules（概要）

global-rules 本身不绑定任何宿主，实现加载方式由各自的 adapter 决定：

- **Cursor 宿主**  
  - 通过工作区根目录下的 `.cursor/rules/*.mdc` 作为入口壳，引导当前会话在对话开始时读取：  
    - `ai-agent-dev-system/global-rules/projects-rules-for-agent.md`  
    - `ai-agent-dev-system/global-rules/skills-rules-for-agent.md`  
  - 具体说明见：`platform-adapters/cursor/rule-loading.md`。

- **VS Code 宿主**  
  - 通过根 `AGENTS.md` 与 `.github/agents/*.agent.md` 说明当前 Agent 角色，并在入口中要求加载上述全局规则文件；  
  - 具体说明见：`platform-adapters/vscode/README.md` 与 `agents-entry.md`。

- **其他宿主 / 第三方插件**  
  - 建议先对照 `platform-adapters/generic/host-capability-checklist.md` 评估能力，再按 `adapter-template.md` 编写适配文档；  
  - 入口位置视宿主而定，但都应在入口中显式引用本目录下的规则文件。

---

## 宿主侧需要做到的最小约定

无论宿主是谁，只要满足以下条件，就可以复用本目录规则：

1. 能为某个 Agent 会话配置「系统级说明 / instructions」；  
2. 在会话开始时，能够让 Agent 读取并遵循：  
   - `OpenSpec.md`；  
   - `global-rules/projects-rules-for-agent.md`；  
   - `global-rules/skills-rules-for-agent.md`；  
3. 在执行具体任务前，为对应角色加载正确的 `agents/*.md` 与 `skills/*/SKILL.md`。

如果某个宿主无法自动达成上述条件，可以通过手动复制规则内容或使用脚本辅助加载，仍然可以遵循同一治理内核。

