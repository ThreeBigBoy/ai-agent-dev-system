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
> `memory/*` 目录中的条目（patterns / anti-patterns / reflections / playbooks / preferences）属于**长期经验层**，不属于规则权威源，只在执行时按需引用；其 frontmatter 与联动规范见 `memory/schema.md`。

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

> **结论级约定：基于 change-id 的智能触发运行后端**  
> 当主 Agent 在任意宿主下收到用户指令时，若同时满足以下条件：  
> - 系统已识别并绑定当前变更的 `change-id`（可由显式具体值解析，或由最近一次绑定/上下文推断获得）；  
> - 同一句话中同时出现两类触发关键词：  
>   - **对象关键词集合**（任一命中即满足）：`提案`、`需求`、`change-id`、`迭代`  
>     - 若句中给出显式的 `kebab-case` change-id 具体值（例如 `sys-trigger-...`），以该具体值绑定；  
>     - 若仅出现字面 `change-id`（无具体值），则以最近一次会话中已绑定的 change-id 为当前绑定；若仍无法绑定，则不触发 heavy（改为引导补齐 change-id 或进入 Step0 需求澄清前确认）。  
>   - **执行动词集合**（任一命中即满足）：`推进`、`落实`、`执行`、`完成`、`验收`、`测试`、`回归`、`归档`、`发布`、`新增`、`新建`、`创建`、`发起`、`这轮变更`、`这个迭代`、`这次发布`  
> - 若识别到显式 change-id 具体值但对应目录（至少包含 `design/documents/[change-id]/` 与 `openspec/changes/[change-id]/` 的 `proposal.md`、`tasks.md` 骨架）不存在，主 Agent 必须先按 OpenSpec 第六节「变更启动顺序」创建骨架目录/文件，再进入 heavy + `run_langgraph`。且  
> - 文本中未明确声明本次为轻量操作（如「先别跑后端」「这次只是随便看下」「仅改文案，不需要协同」），  
> 则主 Agent 应在完成 simple/heavy 判定后，**按 heavy + 运行后端流程执行**：  
> 1. 识别并绑定当前 change-id；  
> 2. 读取对应 `openspec/changes/[change-id]/tasks.md`，按任务章节对应的 Agent 角色构造或更新一份运行决策（如 `agent_decision.json` 或等价决策对象），为需由运行后端承接的任务设置 `executor`；  
> 3. 通过约定入口（如 `agent_team_project` 或其 MCP 封装）触发运行后端，让对应执行角色按 `skills-rules-for-agent.md` 触发技能并完成任务；  
> 4. 运行结束后，在当前项目的 `design/documents/迭代日志.md` 中追加一条包含 change-id、Agent、技能、任务与模型信息的记录。  
> 各业务项目可在自身的 `openspec/AGENTS.md` 中，用自然语言补充示例与偏好（例如如何显式要求/禁止触发运行后端），但不得与上述结论级约定冲突。

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
- **执行管线（V2.11.1）**：默认后端实现 Step 0 需求澄清 → HC0/HC2/HC7 人工确认门控 → parse_tasks → dispatch → collect_feedback；人工确认接口与 MCP 工具见 `README.md` 与 `新用户快速开始.md`；最小验证脚本：`scripts/verify-minimal/verify_minimal.py`。

---

## 记忆（memory）使用约定

- `memory/`：用于存放跨 change-id / 跨项目可复用的模式（patterns）、反模式（anti-patterns）、反思（reflections）、剧本（playbooks）与偏好（preferences），其结构与 frontmatter 规范见：  
  - `memory/README.md`  
  - `memory/schema.md`  
- **职责分工**（与 rules / skills 的关系）：  
  - rules（`OpenSpec.md` 与 `global-rules/*.md`、`agents/*.md`、`skills-rules-for-agent.md`）只回答 When / Who / Must 与极薄的结论级 HOW；  
  - skills（`skills/*/SKILL.md`）回答具体 How to do（步骤、输入输出、产出结构）；  
  - memory（`memory/*`）沉淀「经验与模式」，为 rules 与 skills 提供可复用的背景、最佳实践和坑点，但不改变规则约束本身。  
- **simple / heavy 下的加载原则**（摘要，以 `global-rules/projects-rules-for-agent.md` 与 `.cursor/rules/agent.mdc` 为准）：  
  - simple 任务：可在宿主入口规则 + 少量按需加载的 `memory/` 条目基础上完成，不强制加载完整 rules；  
  - heavy 任务：须按 rules 层要求加载完整 rules + 执行方 `agents/*.md`，在需要 HOW 与经验时再按需加载对应 SKILL 与 memory 条目。  
- **类神经网络式联动与克制机制**：  
  - 对关键记忆条目，可在 frontmatter 中使用 `related` 字段，并在正文中增加「关联模式」小节，形成一跳的簇状联动（如迭代日志 ↔ runtime-logs ↔ rules 演进）；  
  - `memory/schema.md` 要求：单条记忆的 `related` 建议控制在 3–5 条以内，只保留强逻辑耦合的条目，加载时通常只按需读取当前条目及其一跳 `related`，不自动递归遍历，避免在 simple 模式下过度拉取记忆。

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
