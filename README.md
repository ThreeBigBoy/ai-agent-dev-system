# 项目简介：多 Agent 协同开发系统（V2.2 思想）

本仓库是多 Agent 协同开发体系的基础设施仓库，用于把「主 Agent 统筹 + 子 Agent 分工 + Skill 执行 + 运行后端承接」收敛成一套可复用的工程化机制。

- 对**业务项目**而言：它提供 OpenSpec 规范、全局规则与 Skills，作为跨项目可复用的治理内核；  
- 对 **Cursor / VS Code / 第三方插件** 而言：它通过 `platform-adapters/*/` 提供宿主适配方案，而不是把某个宿主写死在规范里。

本 `README.md` 仅作为**总览与导航入口**，不作为治理规则权威源。具体规则、角色、技能和运行约束以仓库内权威文档为准。

---

## 核心思想（自 V2.2 起至 V2.5）：治理内核宿主无关，宿主入口各归其位

在 V2.1 的基础上，V2.2 进一步强调：

- **治理内核层（宿主无关）**  
  - 文件：`OpenSpec.md`、`global-rules/*.md`、`agents/*.md`、`skills/*/SKILL.md`  
  - 职责：定义变更机制、角色边界、技能触发、日志制度、审核与闭环规则。

- **宿主适配层（platform-adapters/*/）**  
  - 文件：`platform-adapters/cursor/*`、`platform-adapters/vscode/*`、`platform-adapters/generic/*`  
  - 职责：描述不同宿主如何加载规则、如何接线 MCP / 扩展、如何实现 decision_sink / runtime_trigger / feedback_bridge / workspace_binding。

- **宿主入口层（各宿主要求的位置）**  
  - 示例：  
    - Cursor：`.cursor/rules/*.mdc`  
    - VS Code：根 `AGENTS.md`、`.github/agents/*.agent.md`  
  - 职责：作为宿主可直接发现的「最薄入口壳」，不再堆叠厚制度正文。

- **运行后端层（可插拔）**  
  - 当前默认实现：`agent_team_project/`  
  - 职责：承接决策写入、执行、反馈与状态持久化；不得改写治理层角色与日志制度。

> 一句话：**OpenSpec + global-rules + agents + skills 定义「怎么办」；platform-adapters 定义「各宿主怎么接线」；运行后端只负责「按决策执行」，不改变规则。**

---

## 规则优先级

本仓库统一采用以下优先级（数值越小优先级越高）：

1. `OpenSpec.md`  
2. `global-rules/*.md`  
3. `agents/*.md`  
4. `skills/*/SKILL.md`  
5. `platform-adapters/*/*.md`  
6. 宿主入口文件（如 `.cursor/rules/*.mdc`、根 `AGENTS.md`、`.github/agents/*.agent.md` 等）  
7. 运行后端实现（如 `agent_team_project/`）

若发生冲突，一律以上位规则为准；宿主入口文件与运行后端不得提升自己为规则来源。

---

## 关键约束（与所有宿主共享）

- **迭代日志**：  
  - 项目级迭代日志采用 OpenSpec 约定的内部目录结构，记录中必须写明当前 `change-id`。  
  - 每次在某一 change-id 上下文中调用 Agent 或 Skill，都应追加一条记录。

- **记录归类**：  
  - 验收记录、评审记录、复盘、对齐结论等应放入 OpenSpec 约定的内部变更记录目录。  

- **治理层角色全集**：  
  - 主 Agent + 产品经理 Agent + 架构 Agent + 前端 Agent + 后端 Agent + 测试 Agent + 文档 Agent + Bug 修复 Agent。  
  - 角色说明见 `agents/README.md` 及各子文件。

- **运行后端（V2.6 升级，V2.11.1 扩展）**：  
  - `agent_team_project/` 是默认运行后端，实现 **LangGraph 独立后端（FastAPI）**：
    - 状态图驱动：`step0_clarification → hc0_gate → parse_tasks → hc2_gate → dispatch → collect_feedback → hc7_gate`，含 Step 0 需求澄清（10 子步骤）与 HC0/HC2/HC7 人工确认门控
    - 检查点持久化：支持断点续跑（`/resume`），状态不丢失
    - 多业务项目：通过 `LANGGRAPH_WORKSPACE_PROJECTS` 配置多项目，按 change_id 自动解析，本仓优先
    - 独立留痕：执行记录写入 `runtime-logs/langgraph-runs/`，不依赖旧三件
    - 人工确认接口：`/confirm/pending`、`/confirm/poll`（Long Poll）、`/confirm/submit`；MCP 工具 `human_confirm_poll`、`human_confirm_submit`
  - 仅覆盖 5 个执行角色（产品经理、架构师、前端工程师、后端工程师、测试工程师），不改变治理层角色全集。

- **运行日志与长期记忆（V2.3 扩展 + V2.4/V2.4.2 渐进加载 + V2.5 主动唤醒与克制）**：  
  - 运行日志：在仓库根级 `runtime-logs/` 下，以 JSON Lines 与文本日志形式记录模型调用的技术指标与系统事件（不记录业务内容），由脚本 `scripts/runtime-logging/append_cursor_model_call.py` 写入，并由各宿主的 `runtime-logging-implementation.md` 文档说明如何触发；  
  - 长期记忆：在根级 `memory/` 目录下，以 frontmatter + Markdown 的形式沉淀跨 change-id 的 patterns / anti-patterns / preferences / playbooks / reflections，由脚本 `scripts/memory/create_memory_entry.py` 创建；  
  - V2.4：规则瘦身与 memory 化，simple/heavy 下渐进加载（简单任务用会话上下文与相关 memory，重规则任务再加载完整 global-rules 与 agents）；  
  - **V2.5 主动记忆唤醒与执行约束**：  
    - **主动记忆唤醒**：主 Agent 在每次任务启动并完成 simple/heavy 判定后，按任务类型与上下文**主动**检索并按需加载相关 memory 条目（见 `agents/主Agent.md` 第 7 条与「运行日志与长期记忆」下列出的关键 memory 路径），不依赖用户提醒；  
    - **改规则层必走 checklist**：凡涉及修改 `global-rules/*.md`、`agents/*.md`、`skills-rules-for-agent.md` 等规则层文件时，主 Agent 在实际改动前**必须先读取** `memory/patterns/pattern-rules-and-memory-evolution-governance.md` 并按其中 checklist 执行（含 change-id 挂载、design/records、迭代日志、以及 README / 新用户快速开始 / 宿主 SOP 是否需同步更新）；  
    - **memory 克制机制**：单条记忆的 `related` 建议 3～5 条、只做一跳加载不递归遍历，详见 `memory/schema.md`。

- **模型使用策略**：  
  - 白名单宿主（当前为 Cursor 官方、VS Code 官方 / GitHub Copilot）下，主 Agent 与子 Agent 均优先使用宿主内置模型；  
  - 第三方宿主（当前明确支持 Continue、OpenAI-Codex）下，主 Agent 优先使用宿主内置模型，但子 Agent / 运行后端直接走个人自定义 OpenAI 兼容 API 模型调度策略；  
  - 若宿主内置模型无响应、异常或不可用，再按对应 adapter / runtime 配置降级到个人自定义 OpenAI 兼容 API 模型链路；  
  - 具体到 Cursor 宿主下的当前映射与模型名单，见 `platform-adapters/cursor/*` 与 `agent_team_project/runtime_config.json`。

---

## 新管线运行架构（V2.6 LangGraph 独立后端，V2.11.1 扩展）

从 V2.6 起采用 **LangGraph 独立后端**；V2.11.1 起管线含 **Step 0 需求澄清** 与 **HC0/HC2/HC7 人工确认门控**：

```
┌─────────────────────────────────────────────────────────────┐
│                      Cursor / VS Code                       │
│  ┌─────────────────┐      ┌─────────────────────────────┐  │
│  │   用户消息       │─────▶│   扩展检测 change-id + 关键词  │  │
│  └─────────────────┘      └─────────────────────────────┘  │
│                              │                              │
│                              ▼                              │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  MCP 工具 / HTTP: POST /run · /confirm/pending · poll ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ HTTP / JSON
┌─────────────────────────────────────────────────────────────┐
│                  LangGraph 独立后端 (FastAPI)                │
│  StateGraph (V2.11.1): step0_clarification → hc0_gate →      │
│  parse_tasks → hc2_gate → dispatch → collect_feedback → hc7_gate
│  ┌─────────────┐  ┌─────────┐  ┌──────────────┐  ┌────────┐ │
│  │ Step 0 需求 │─▶│ HC0 门  │─▶│ parse_tasks  │─▶│ HC2 门 │→ … │
│  │ 澄清(10步)  │  │ (人工)  │  │ (Step1-4检查) │  │ (人工) │   │
│  └─────────────┘  └─────────┘  └──────────────┘  └────────┘   │
│  ┌──────────┐  ┌──────────────┐  ┌─────────┐                   │
│  │ dispatch │─▶│ collect_fb   │─▶│ HC7 门  │→ END               │
│  └──────────┘  └──────────────┘  │ (验收)  │                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ 调用 executor
┌─────────────────────────────────────────────────────────────┐
│                    API 模型 (SiliconFlow等)                   │
└─────────────────────────────────────────────────────────────┘
```

**核心特点**：
- **状态图驱动**：Step 0 → HC0 → parse_tasks → HC2 → dispatch → collect → HC7 强制流转，100% 无跳过
- **人工确认门控**：HC0（需求澄清后）/ HC2（方案确认后）/ HC7（验收前）需落盘确认文件或调用 `/confirm/submit`
- **检查点持久化**：内置 `MemorySaver`（MVP）/ Redis（生产），支持断点续跑（`/resume` 接口），状态不丢失
- **多业务项目支持**：通过 `LANGGRAPH_WORKSPACE_PROJECTS` 配置多项目（JSON 数组或扁平串 `key|path:key2|path2`），按 change_id 自动解析
- **本仓优先**：后端始终先查本仓 `openspec/changes/`，再按列表顺序尝试业务项目
- **独立留痕**：执行记录写入 `runtime-logs/langgraph-runs/YYYY-MM-DD.jsonl`，不依赖迭代日志或 design/documents
- **启动诊断与最小验证**：`scripts/diagnose_startup/diagnose_startup.py` 六项环境检查；`scripts/verify-minimal/verify_minimal.py` 可从头到尾自检管线（见 `新用户快速开始.md` 5.2）

**与旧机制对比**：
| 维度 | 旧机制（已废弃） | 新管线（V2.6） |
|------|------------------|----------------|
| 执行保障 | 文件驱动，易跳过 | 状态图强制流转 |
| 状态恢复 | 会话级，易丢失 | 检查点持久化，可断点续跑 |
| 多项目 | 单路径配置 | 项目列表，自动解析 |
| 留痕位置 | `agent_decision.json` / `agent_feedback.txt` / `agent_skill.log` | `runtime-logs/langgraph-runs/` |

---

## 仓库结构概览

- `OpenSpec.md`  
  项目宪法与变更机制，定义 change-id、文档目录、变更启动顺序和基础协作规则。

- `global-rules/`  
  全局规则目录入口。  
  - `projects-rules-for-agent.md`：项目通用规则、变更入口、自检与迭代日志要求，**只回答「谁/何时/必须做什么」与极薄结论级 HOW**，更详细的执行步骤与示例统一由 `skills/*/SKILL.md` 与 `memory/` 承接；  
  - `skills-rules-for-agent.md`：Agent 与 Skills 映射及触发约定，负责「角色 ↔ 技能」矩阵与「先读 SKILL 再执行」约束；  
  - `readme-rules-for-agent.md`：README 编写与维护规范，多为 SHOULD 级建议。

- `agents/`  
  角色治理层说明，定义主 Agent 与各子 Agent 的职责边界，以及与运行后端的关系。

- `skills/`  
  每个技能目录下的 `SKILL.md` 与 REFERENCE 约定具体执行步骤和产出物最低结构。

- `platform-adapters/`  
  宿主适配层文档：  
  - `platform-adapters/cursor/*`：Cursor 规则加载、MCP 接线、反馈桥等；  
  - `platform-adapters/vscode/*`：VS Code Agent Chat 入口与模式映射；  
  - `platform-adapters/generic/*`：第三方插件的能力检查清单与适配模板。

- `runtime-logs/`  
  运行日志体系根目录，包含：
  - `runtime-logs/README.md`：字段约定与宿主适配说明；  
  - `model-calls/`：按日期分片的 JSON Lines 模型调用日志；  
  - `system-events/`：系统事件文本日志；  
  - `adapters/`：各宿主如何采集并写入运行日志的说明（cursor/vscode/generic 等）。

- `memory/`  
  长期记忆库根目录，包含：
  - `memory/README.md`：记忆库定位与使用方式；  
  - `memory/schema.md`：frontmatter 字段规范；  
  - `patterns/`、`anti-patterns/`、`preferences/`、`playbooks/`、`reflections/` 等子目录，用于按类型存放长期记忆条目（包括规范体系概览、规则执行模拟与反思、配额治理实践等抽象经验）。

- `scripts/runtime-logging/` 与 `scripts/memory/`  
  运行日志与长期记忆的辅助脚本目录：
  - `scripts/runtime-logging/append_cursor_model_call.py`：向 `runtime-logs/model-calls/*.jsonl` 追加一条模型调用记录的统一脚本接口；  
  - `scripts/memory/create_memory_entry.py`：在 `memory/*/` 下创建带 frontmatter 的长期记忆条目的统一脚本接口。

- `AGENTS.md`  
  根级别的多宿主 Agent 说明与规则优先级，供 VS Code 等支持根 AGENTS 的宿主加载。

- `agent_team_project/`  
  默认运行后端说明与实现（可选用），实现决策执行与反馈。

- `新用户快速开始.md`
  新用户从 Git 下载仓库后，按宿主选择初始化手册并完成首次 GUI 走查的总入口。

---

## 建议阅读顺序

1. **理解规范与变更机制**：  
   - `OpenSpec.md`
2. **理解任务执行机制与技能映射**：  
   - `global-rules/projects-rules-for-agent.md`  
   - `global-rules/skills-rules-for-agent.md`
3. **理解多 Agent 角色治理边界**：  
   - `AGENTS.md`（根）  
   - `agents/主Agent.md`  
   - `agents/README.md`
4. **如需理解默认执行链路**：  
   - `agent_team_project/README.md`  
   - `platform-adapters/cursor/*`（若在 Cursor 宿主下使用）
5. **如需快速上手某一宿主**：
   - `新用户快速开始.md`

补充说明：

- V2.1 / V2.2 的详细重构背景、内部验收记录和设计推演资料属于维护者内部资料，默认不作为新用户入口公开依赖。  
- 新用户按本 README、`AGENTS.md`、`OpenSpec.md` 与各宿主 SOP 即可完成初始化与使用。

---

## 更新日志

- **V2.0**  
  - Cursor + LangGraph + 自定义 Skill + 本地插件，实现「决策 → 执行 → 反馈 → 调整」近全自动闭环。  
  - 以 MCP `write_decision` 为主写入决策并做 JSON schema 校验，避免自然语言约束写文件的可靠性问题。  
  - 插件监听反馈文件 → 复制到剪贴板 → 提示用户在 Chat 中粘贴（降级方案）。  
  - 明确 `agent_team_project` 目录结构：`run_skill.py`、`dynamic_agent_skill.py`、决策/反馈文件、`.vscode/extensions` 下反馈插件。

- **V2.1**  
  - 治理层（OpenSpec + global-rules + agents + skills）为唯一权威；`agent_team_project` 仅作默认运行后端，不再参与规范定义。  
  - 入口瘦身：`.cursor/rules/agent.mdc` 仅做总指挥入口与优先级声明，不堆厚制度正文。  
  - 统一日志口径为项目级 `design/documents/迭代日志.md`。  
  - 明确默认 backend 的 5 个 executor 与治理层角色全集区分（主 Agent、文档 Agent、Bug 修复 Agent 不进入 executor 枚举）。

- **V2.2**  
  - 治理内核宿主无关；宿主专属内容下沉到 `platform-adapters/*`（cursor / vscode / generic），各宿主入口做「最薄入口壳」。  
  - 运行协议抽象为 decision_sink、runtime_trigger、feedback_bridge、workspace_binding；文件命名统一为 `agent_decision.json`、`agent_feedback.txt`。  
  - 白名单宿主（Cursor、VS Code）与第三方宿主（Continue、OpenAI-Codex）的模型策略区分，通过 `AGENT_HOST_TYPE` 与 `runtime_config.json` 配置。  
  - 支持四宿主初始化 SOP 与新用户快速开始总入口；反馈闭环时主 Agent 须写收尾决策以显式标记本轮结束。

- **V2.3（运行日志与长期记忆）**  
  - 在仓库根级新增 `runtime-logs/` 运行日志体系：  
    - `model-calls/*.jsonl` 记录按 change-id/Agent 维度的模型调用技术指标（host、model_family、status、tokens、duration 等）；  
    - `system-events/events.log` 记录关键运行事件；  
    - 通过 `scripts/runtime-logging/append_cursor_model_call.py` 提供统一写入接口，并在各宿主 adapter 中给出触发说明。  
  - 在仓库根级新增 `memory/` 长期记忆库：  
    - 通过 frontmatter 标记记忆类型（pattern/anti-pattern/preference/playbook/reflection）、适用项目/宿主与来源 change-id；  
    - 使用 `scripts/memory/create_memory_entry.py` 生成带骨架正文的记忆条目，供主 Agent 在复盘阶段按规则沉淀。  
  - 在 `agents/主Agent.md` 中补充「运行日志与长期记忆」规则：  
    - 定义何时记录 runtime-logs（基于 change-id 关键节点、基础设施/成本相关变更、错误/限流等）；  
    - 定义 memory 候选判定与类型区分（含 preference 写入前需用户确认）；  
    - 约定主 Agent 通过统一脚本接口与宿主 adapter 触发 runtime-logs 与 memory 的写入。  
  - 在 `platform-adapters/*` 与各宿主从 0 初始化 SOP 中，增补对 `runtime-logs/` 与 `memory/` 能力的「进阶能力」说明，保持治理层统一、宿主实现可插拔。

- **V2.4（规则与 know-how 轻量化 + memory 化） / V2.4.2（rules × memory 瘦身新标准）**  
  - 清理与收束早期 `know-how/` 目录，将规范体系总览与规则执行模拟等长文抽取为 `memory/` 条目（如 `pattern-spec-system-overview-v2-4.md`、`reflection-agent-execution-simulation-v2-4.md`），并在运行路径中移除原长文，避免与最新规则/记忆并存造成混淆；  
  - 将全局规则加载从「首轮强制读完整 `projects-rules-for-agent.md` + `skills-rules-for-agent.md`」调整为依据 simple/heavy 任务模式渐进加载：简单任务优先使用现有会话上下文与相关 memory，重规则任务再加载完整 global-rules 与 agents 文档；  
  - 在 `projects-rules-for-agent.md` 等规则文件中，将 SHOULD 及更低等级内容收束为概要与 memory 检索指引，详细示例、执行模拟与配额治理实践逐步迁移到 `memory/`，让治理层正文保持以 MUST 为主、结构更瘦、上下文占用更可控；  
  - 在 V2.4.2 中进一步明确：rules 只保 When/Who/Must + 结论级 HOW，具体 HOW 与模版由 SKILL 与 memory 承接，并要求在规则演进时同步审视 README、`新用户快速开始.md` 与各宿主 SOP 是否需更新。

- **V2.5（主动记忆唤醒与执行机制强化）**  
  - 主 Agent 增加「主动记忆唤醒」：每次任务启动并完成 simple/heavy 判定后，按任务上下文主动检索并按需加载相关 memory（迭代日志、runtime-logs、规则演进等关键条目），不依赖用户外部提醒；关键 memory 路径在 `agents/主Agent.md` 的「运行日志与长期记忆」下显式列出。  
  - 改规则层强制钩子：在 `.cursor/rules/agent.mdc` 中约定，凡修改 `global-rules/*.md`、`agents/*.md`、`skills-rules-for-agent.md` 前必须先读 `memory/patterns/pattern-rules-and-memory-evolution-governance.md` 并执行其 checklist（含 README/SOP 审视），不得跳过。  
  - memory 联动与克制：memory 条目间通过 frontmatter `related` 与正文「关联模式」形成一跳簇状联动；`memory/schema.md` 明确克制机制（3～5 条 related、按需一跳加载、不递归遍历）。  
  - 宿主入口与全局规则入口瘦身：`agent.mdc`、`global-rules.mdc` 仅保留身份/指向与强制钩子，具体 simple/heavy 与执行方判定规则不重复，见 `projects-rules-for-agent.md` 与 `agents/主Agent.md`。  
  - `AGENTS.md` 补充「记忆（memory）使用约定」与规则优先级中对 memory 的定位。  
  - **场景→必读 memory/清单的通用执行保障**：新增 `memory/patterns/pattern-scenario-memory-trigger-governance.md`，定义「治理关键场景 → 必读 memory / 必做 checklist」绑定表（改规则、收尾、写 runtime-logs、新建变更、判定 simple/heavy、新增 memory、提交前 review 等），并在 `agents/主Agent.md`、`projects-rules-for-agent.md`、`.cursor/rules/agent.mdc` 中补全各场景的触发与必读要求，使正确行为由结构化绑定保障而非临时记忆。

- **V2.6（LangGraph 独立后端 - 架构级升级）**  
  - **核心升级**：从「宿主级约定」到「框架级强制保障」，解决规则命中但不执行、竞态与重复执行、跨会话状态丢失三大痛点。
  - **新执行管线（LangGraph + FastAPI）**：
    - LangGraph StateGraph：`parse_tasks → dispatch → collect_feedback` 强制流转，无断点
    - FastAPI 服务：`POST /run`、`GET /status/{change_id}`、`GET /health`、`POST /resume`（断点续跑）
    - 检查点持久化：`MemorySaver`（MVP）/ Redis（生产），支持从任意节点恢复执行
  - **多业务项目支持**：
    - 配置范式：`LANGGRAPH_WORKSPACE_PROJECTS` 支持 JSON 数组或扁平串（`key|path:key2|path2`）
    - 本仓优先：后端始终先查本仓 `openspec/changes/`，再按列表顺序、按 change_id 自动解析命中项目
    - 无需「当前项目」配置：多项目时自动选择包含该 change 的第一个项目，也可选 `LANGGRAPH_CURRENT_PROJECT_KEY` 固定当前项目
  - **独立留痕体系**：新管线执行记录写入 `runtime-logs/langgraph-runs/YYYY-MM-DD.jsonl`，含 `ts/change_id/thread_id/workspace_root/project_key/status/task_count/latency_seconds/checkpoint_id/error`，不依赖迭代日志或 design/documents 做执行审计。
  - **旧管线废弃**：`agent_decision.json` / `agent_feedback.txt` / `agent_skill.log` 不再使用（走新管线时为空是预期行为）。
  - **MCP 集成**：`run_langgraph(change_id, task_range?, workspace_root?)` 工具封装 HTTP /run 调用，返回格式化 feedback 注入对话。
  - **记忆沉淀**：新增 `pattern-langgraph-mcp-multi-workspace-config.md`（多项目配置范式）、`pattern-new-pipeline-trace-vs-design-documents.md`（新管线留痕与 design 职责分离）。

- **V2.7（目录结构与质量闭环规范化）**
  - **目录结构规范**：建立 `design/documents/changes/[change-id]/` 目录结构，统一存放 PRD、技术方案、架构图、评审记录等产出物
  - **8+1 质量闭环 v1.0 建立**：从需求分析到复盘的 8 步完整质量闭环，每步定义准入准出标准、产出物要求
  - **PRD 命名规范**：`PRD-[change-id]-[关键词].md` 统一命名格式
  - **新建核心 Skill**：
    - `prd-review/SKILL.md`：PRD 评审技能，定义评审流程和判定标准
    - `architecture-review/SKILL.md`：技术方案评审技能，架构评审规范
    - `retrospective-analysis/SKILL.md`：复盘技能，5阶段复盘法
  - **质量门禁机制**：每个阶段出口设置强制检查，确保产出物完整性

- **V2.8（check-langgraph-backend 二期：阶段化执行架构升级）**
  - **阶段化执行架构**：解决 LangGraph 后端超时问题，重构自检脚本支持分阶段执行
  - **Phase 配置体系**：`DEFAULT_PHASES` 定义 env-check/mcp-check/biz-trace/full 四个 phase
  - **自检脚本重构**：`check_langgraph_backend.py` 支持按 phase 多次短调用 + 结果聚合
  - **Server 端改造**：`server.py` 支持 phase 参数传递和阶段化留痕
  - **Workflow 改造**：`workflow.py` AgentState 支持 phase 过滤任务
  - **模式沉淀**：创建 `pattern-phase-execution.md`（阶段化执行架构模式）
  - **完整质量闭环实战**：按 8+1 流程完成 PRD 评审 → 技术方案 → 编码 → 代码评审 → 验收 → 归档 → 复盘
  - **评审修复循环发现**：发现「有条件通过」处理机制缺失，启动框架级改进

- **V2.9（10 步质量闭环 v1.3 + 执行质量保障机制）**  
  - **核心升级**：10 步质量闭环 v1.3（原8+1升级为10步），建立完整的执行质量保障机制，防止术语定义漂移、惯性思维陷阱、规范执行衰减、孤立改进。
  - **Step 10 全局检查与联动更新（v1.3 新增）**：
    - 新增 Step 10「全局检查与联动更新」，确保变更后所有关联文档同步更新
    - 6类文档检查清单：根级/宿主SOP/Agent/规则/Skill/Memory
    - 不得声称「全局检查完成」直到全部15项检查通过
    - 创建 `preference-coordinated-update-checklist.md`、`anti-pattern-isolated-improvement.md`
  - **评审修复循环机制**：
    - 明确「有条件通过」≠「可以进入下一阶段」，必须修复后重新评审
    - 升级 `code-review/SKILL.md` v1.1、`func-test/SKILL.md` v1.1，明确修复循环流程
    - 创建 `pattern-review-fix-loop.md`、`anti-pattern-conditional-pass-as-go.md`
  - **Step 8 归档操作规范化**：
    - 明确归档 = 合并 specs/ + 移动 changes/ 到 archive/，而非简单"标记完成"
    - 升级 `pattern-complete-quality-closed-loop.md` Step 8 v1.1，增加 4 阶段归档操作
    - 创建 `preference-archive-operation-checklist.md`，11 项检查清单
  - **执行前查阅规范机制**：
    - 在 `skills-rules-for-agent.md` 新增第十章，强制要求执行前完成 4 项查阅
    - Skill 版本确认、术语定义查阅、关联 Memory 唤醒、质量门禁检查清单查阅
  - **规范衰减防护机制**：
    - 在 `pattern-complete-quality-closed-loop.md` v1.2 新增防护机制章节
    - 执行前强制检查、阶段出口强制检查、定期回顾检查、自动化防护
  - **质量门禁自动化工具**：
    - 开发 `openspec_validate.py` v1.0（基础验证）和 v2.0（质量门禁自动化）
    - 支持术语使用检查、Skill 版本检查、迭代日志格式验证、阶段统计
  - **Memory 自动唤醒优化**：
    - 创建 `preference-memory-auto-awakening.md`，定义三层唤醒策略
    - Skill-Memory 映射表、关键词触发机制、优先级排序算法
  - **复盘机制常态化**：
    - 创建 `playbook-retrospective-routine.md`，定义三种复盘触发机制
    - 定期复盘（每周/每迭代）、事件触发复盘、问题驱动复盘
  - **术语表与自动链接**：
    - 创建 `preference-terminology-glossary.md`，汇总 50+ 核心术语的规范定义
    - 术语定义、来源、常见偏差、正确理解、自动链接映射
  - **全局检查与联动更新**：
    - 建立变更影响分析机制，确保升级时同步更新相关文档
    - 同步更新「新用户快速开始.md」和4个宿主SOP，增加质量保障机制简介章节

- **V2.11.1（Step 0 需求澄清 + 人工确认门控 + 最小验证）**  
  - **Step 0 需求澄清层**：Workflow 增加 `step0_clarification`（10 个子步骤 prompt + 跳过/重做）+ `hc0_gate`（Step 0 与 Step 1 之间人工确认）；`agent_team_project/langgraph_backend/step0_prompts/` 与 `openspec/changes/.../step0_checkpoints.md` 定义准入/准出。  
  - **人工确认门控**：HC0/HC2/HC7 门控节点；后端 `/confirm/pending`、`/confirm/poll`（async Long Poll）、`/confirm/submit`；MCP 工具 `human_confirm_poll`、`human_confirm_submit`；前端 `frontend/src/components/ConfirmPanel.tsx`。  
  - **启动诊断**：`scripts/diagnose_startup/diagnose_startup.py` 六项检查（磁盘/Python/内存/网络/配置/端口），支持表格与 JSON 输出。
  - **最小验证脚本**：`scripts/verify-minimal/verify_minimal.py` 可从头到尾自检管线（诊断 + Workflow 场景 A/B，可选 HTTP），供人工验收使用。
  - **生产就绪与可扩展**：安全/稳定/观测/边界/Discovery 等模块实现见 `openspec/changes/deepen-langgraph-v2-11-1/`。

---

## 使用方式

- **作为人类读者**：  
  - 把本文件当作仓库导航页，用于快速找到治理内核文档、宿主 adapter 文档与运行后端说明。

- **作为 AI 协作入口**：  
  - 实际身份、行为和执行约束以 `OpenSpec.md`、`global-rules/`、`agents/`、`skills/` 为准；  
  - 宿主如何加载这些规则，由对应的 `platform-adapters/*/` 与入口文件（如 `.cursor/rules/*.mdc`、根 `AGENTS.md`）决定；  
  - 本文件不直接驱动执行逻辑，只提供整体视图与导航。
