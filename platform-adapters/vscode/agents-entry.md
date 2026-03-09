## VS Code 入口文件说明（agents-entry）

在 V2.2 中，VS Code 宿主推荐通过以下两类入口文件接入 ai-agent-dev-system：

- 根 `AGENTS.md`：作为 VS Code 官方 Agent Chat 的 always-on instructions 入口；  
- `.github/agents/*.agent.md`：作为不同 Agent 模式（主 Agent、前端 Agent、后端 Agent、测试 Agent 等）的轻量入口。

### 1. 根 `AGENTS.md` 的职责

- 向宿主 Agent 解释本仓库的整体结构：  
  - 治理内核：`OpenSpec.md`、`global-rules/*.md`、`agents/*.md`、`skills/*/SKILL.md`；  
  - 宿主适配层：`platform-adapters/*/`；  
  - 运行后端层：`agent_team_project/`（可选使用）。
- 要求 Agent 在响应用户任务前：  
  - 先读取并遵循 `global-rules/projects-rules-for-agent.md` 与 `global-rules/skills-rules-for-agent.md`；  
  - 将自身视为「主 Agent（总指挥）」或由用户指定的子 Agent 角色；  
  - 按 `skills-rules-for-agent.md` 为对应角色选择 Skill，并在执行前读取对应 `SKILL.md`。

### 2. `.github/agents/*.agent.md` 的职责

建议为典型角色建立以下入口文件（命名仅为示例，可按 VS Code 要求调整）：

- `.github/agents/main.agent.md`：主 Agent（总指挥）模式；  
- `.github/agents/frontend.agent.md`：前端 Agent 模式；  
- `.github/agents/backend.agent.md`：后端 Agent 模式；  
- `.github/agents/test.agent.md`：测试 Agent 模式。

每个入口文件只需做三件事：

1. 声明自己的角色（主 Agent / 某个子 Agent）；  
2. 引用治理内核规则与对应 `agents/*.md` 文件；  
3. 指明与自身角色相关的主导/联动技能（参见 `global-rules/skills-rules-for-agent.md`），并要求在执行前读取对应 `SKILL.md`。

### 3. 内容边界

- 不在入口文件中重复粘贴大段治理制度正文；  
- 不在入口文件中描述运行后端的全部实现细节；  
- 详细规则统一放在：  
  - `OpenSpec.md`  
  - `global-rules/*.md`  
  - `agents/*.md`  
  - `skills/*/SKILL.md`  
  - `platform-adapters/vscode/*.md`（本目录）

