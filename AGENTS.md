# 仓库定位：多宿主、多 Agent 的治理内核

本仓库 `ai-agent-dev-system` **不是单一业务项目**，而是一个可被多个 IDE / Agent 平台复用的「多 Agent 协同开发治理内核」：

- 把「主 Agent 统筹 + 子 Agent 分工 + Skill 执行 + 运行后端承接」沉淀为一套可复用规则；
- 通过 `OpenSpec.md`、`global-rules/*.md`、`agents/*.md`、`skills/*/SKILL.md` 定义**与宿主无关**的规范；
- 通过 `platform-adapters/*/` 为 Cursor / VS Code / 其他宿主提供接线文档与入口模板；
- 运行后端（如 `agent_team_project/`）只是一种可替换的执行实现。

本文件作为跨宿主的总入口说明，供 VS Code 等支持根 `AGENTS.md` 的宿主直接加载。

---

## 规则优先级（V2.2）

当多个文档对同一问题给出约束时，应按以下优先级裁决（数值越小优先级越高）：

1. `OpenSpec.md`  
2. `global-rules/*.md`  
3. `agents/*.md`  
4. `skills/*/SKILL.md`  
5. `platform-adapters/*/*.md`  
6. 宿主入口文件（如 `.cursor/rules/*.mdc`、根 `AGENTS.md`、`.github/agents/*.agent.md` 等）  
7. 运行后端实现（如 `agent_team_project/`）  
8. 用户本机配置（如 `~/.cursor/mcp.json`、插件设置、快捷键设置等）

> 说明：宿主入口文件和本机配置只负责「如何加载与接线」，**不得提升自身为规则权威源**；若与治理内核冲突，一律以 1–4 层为准。

---

## Agent 角色与 Skills 映射

本仓库的多 Agent 体系由 `agents/` 与 `skills/` 共同定义：

- 角色说明见：`agents/README.md` 与各子文件（如 `agents/主Agent.md`、`agents/子Agent-前端.md` 等）；  
- 角色与技能映射见：`global-rules/skills-rules-for-agent.md`；
- 各技能的执行细节见：`skills/*/SKILL.md`。

**约定（所有宿主通用）：**

1. 主 Agent 负责统筹、任务拆解、分工与闭环，**默认不直接执行具体技能**；  
2. 每当某个子 Agent 被指派执行任务时：
   - 先根据 `skills-rules-for-agent.md` 找到该角色的主导/联动技能；  
   - 再读取对应 `skills/<技能名>/SKILL.md`，按其中步骤执行；  
   - 执行完成后，将结果落到 OpenSpec / design 约定的路径，并在 `design/documents/迭代日志.md` 追加记录。

---

## 在本仓库中工作的约定

当当前工作区根目录就是 `ai-agent-dev-system` 时（例如用 Cursor / VS Code 打开本仓库本身）：

- **change-id 归属**  
  - 所有与治理内核演进相关的任务，默认为属于 `project-early-phase`；  
  - 若你为某次大版本演进创建了独立的 `change-id`，应在 `design/documents/[change-id]/` 与 `openspec/changes/[change-id]/` 下组织文档与任务。

- **任务执行**  
  - 新需求 / 新改造：按 `OpenSpec.md` 第六节与 `global-rules/projects-rules-for-agent.md` 的「变更启动顺序」执行；  
  - 日常文档与规则微调：也应归属于某个 change-id，并在 `design/documents/迭代日志.md` 中追加记录。

- **宿主无关原则**  
  - 在本仓库内改写规则或文档时：  
    - 应优先使用宿主无关术语（如 `decision_sink`、`runtime_trigger`、`feedback_bridge`、`workspace_binding`）；  
    - 各宿主的具体接线方式，请写入 `platform-adapters/<host>/`，而不是直接写入治理内核文档。

## 模型使用约定

- 白名单宿主（当前为 Cursor 官方、VS Code 官方 / GitHub Copilot）下，主 Agent 与子 Agent 优先使用宿主内置模型能力。  
- 第三方宿主（当前明确支持 Continue、OpenAI-Codex）下，主 Agent 优先使用宿主内置模型，但子 Agent / 运行后端执行链路直接走个人自定义 OpenAI 兼容 API 模型调度策略。  
- 若宿主内置模型无响应、异常或不可用，可降级到个人自定义 OpenAI 兼容 API 模型链路。  
- 个人 API 模型的具体提供方、Base URL、候选模型与优先级，应写入对应宿主 adapter 或运行后端配置，而不直接散落在治理内核正文中。  
- 对当前 Cursor 默认运行后端，见：
  - `platform-adapters/cursor/README.md`
  - `platform-adapters/cursor/mcp-setup.md`
  - `agent_team_project/runtime_config.json`

---

## 作为其他项目的全局规则来源时

当某个业务项目引用本仓库作为 OpenSpec / 多 Agent 的全局规则来源时，应遵循：

1. 在该业务项目根目录按 OpenSpec 要求创建 `openspec/`，并维护自己的 `openspec/AGENTS.md` 与 `openspec/project.md`；  
2. 在业务项目的 `openspec/AGENTS.md` 中，明确：
   - 可调用的 `ai-agent-dev-system/skills/*` 及触发词/路径；  
   - 需要额外遵循的 `ai-agent-dev-system/global-rules/*.md`；  
3. 在实际协作中：
   - 优先读取业务项目自身的 `openspec/AGENTS.md` 与 `openspec/project.md`；  
   - 同时遵循本仓库的 `OpenSpec.md`、`global-rules/*.md`、`agents/*.md` 与 `skills/*/SKILL.md`。

宿主如何加载这些规则（Cursor / VS Code / 其他），请参考 `platform-adapters/*/` 下对应 adapter 文档。
