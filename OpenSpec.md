# OpenSpec 开发规范

> 规范驱动开发（Spec-Driven Development）的长期、多项目可复用知识库。  
> 适用于任意代码仓库，可与 AI 协作时配合 `openspec/` 目录使用。

本文档（`/ai-agent-dev-system/OpenSpec.md`）是**驱动所有项目开发的原始规范**，可复用于所有项目。  
补充规范、技能与项目内文档的定位及 AI 协作时的引用关系见下节「文档定位与 AI 协作关系」。

---

## 一、文档定位与 AI 协作关系

### 1.1 文档与目录定位

| 文档/目录 | 定位说明 |
|-----------|----------|
| **`/ai-agent-dev-system/OpenSpec.md`** | 驱动所有项目开发的**原始规范**，复用于所有项目；详见本文档正文。 |
| **`/ai-agent-dev-system/global-rules/projects-rules-for-agent.md`** | 驱动所有项目开发的**补充规范**（作为 OpenSpec.md 的补充），复用于所有项目。 |
| **`/ai-agent-dev-system/global-rules/readme-rules-for-agent.md`** | 驱动所有项目开发的**补充规范**（作为 OpenSpec.md 的补充），复用于所有项目。 |
| **`/ai-agent-dev-system/global-rules/skills-rules-for-agent.md`** | 驱动所有项目开发的**补充规范**（作为 OpenSpec.md 的补充），复用于所有项目。 |
| **`/ai-agent-dev-system/skills/`** | 与 AI 协作时 Agent 可调用的所有 Skills，复用于所有项目。 |
| **`/openspec/AGENTS.md`** | 在某个项目根目录新增 `openspec/` 后，复制本规范中的目录结构，并根据**项目类型**、结合 OpenSpec.md（作为规范与上下文）填写；为 AI 工作说明书，约定可调用的 Skills、需遵循的全局规则等。 |
| **`/openspec/project.md`** | 同上，在项目根目录 `openspec/` 下；结合 OpenSpec.md 与项目类型填写。**本项目整体宪法规范**：约定项目定位、架构模式、技术栈、目录与命名等顶层规则。 |
| **`/design/project-rules/`** | 某个项目内目录，存放**工程宪法（project.md）的补充**：对技术实现、格式与流程的细化；与 `project.md` 共同构成完整约定体系，实现与评审时须同时遵守。 |
| **`/design/documents/`** | 某个项目内目录，存放项目背景、MVP 产品方案、功能需求说明书、技术方案说明书、验收 Checklist 等。按变更组织的子目录 `design/documents/[change-id]/` 下可含需求与验收相关文档；**功能验收/测试记录**建议文件名 `[change-id]-func-test.md` 或 `func-test.md`，**代码评审记录**建议文件名 `[change-id]-code-review.md`，均存放于 **`design/documents/[change-id]/records/`**，与需求、验证清单同属该变更，便于按变更聚合与归档。以「反思-」「复盘-」「对齐结论」、「XX验收记录」、「XX测试记录」等命名的过程反思、复盘、对齐结论及验收/测试记录类文档也应置于 **`design/documents/[change-id]/records/`**。**项目级迭代日志文档**（**强制要求**，适用于所有采用本规范的项目与所有变更/迭代）统一为单一文件 `design/documents/迭代日志.md`，记录所有 change-id（含 `project-early-phase`）的 Agent/技能调用；每次在某一 change-id 上下文中调用 `agents/` 下 Agent 或 `skills/` 下技能时**须在该文件追加一条记录**（记录内容中必须包含本次 change-id），格式见 `projects-rules-for-agent.md`「Agent 与技能调用迭代日志」。`design/documents/[change-id]/records/` 继续用于收纳该变更的验收、评审、复盘与对齐结论等记录类文档，不再作为主迭代日志口径。 |
| **`/scripts/`** | 某个项目根目录下的**标准子目录**，统一存放该项目的自动化脚本（如本地初始化、数据/配置迁移、一致性修复、工具型脚本等）；脚本应在 `scripts/README.md` 或各自子目录的 README 中说明用途与用法，其命名与目录结构须受本项目 `openspec/project.md` 与 `design/project-rules/` 约束，避免在项目根目录散落零散脚本文件。 |

### 1.2 AI 协作时文档引用与上下文关系

- **新项目第一件事**：在项目根目录创建 `openspec/`，复制本规范（OpenSpec.md）中的目录结构时，**严格遵循 OpenSpec.md**，并根据 openspec 规范与项目类型填写 `AGENTS.md` 与 `project.md`。
- **填写 AGENTS.md 与 project.md 时**：优先引用 `openspec/` 下的规范与提案，**同时严格遵循 OpenSpec.md**。
- **AGENTS.md 中必须明确**：
  - 可调用的 **`/ai-agent-dev-system/skills/`** 中的技能（及触发词/路径）；
  - 需要额外遵循的 **`/ai-agent-dev-system/global-rules/`** 中的全局规则。
- **project.md 中必须明确**：
  - 额外需严格遵循的 **`/design/project-rules/`** 下的文档（作为工程宪法 project.md 的补充约束），实现与评审时与 project.md 一并遵守。

---

## 二、核心概念

| 概念 | 含义 | 对应目录 |
|------|------|----------|
| **Specs（规范）** | 已实现的功能 | `openspec/specs/` |
| **Changes（变更）** | 待实施的提案 | `openspec/changes/` |
| **Archive（归档）** | 已完成并部署的变更 | 通过 `openspec archive` 归档后更新 specs |

---

## 三、OpenSpec 文件结构

### 3.1 根目录结构

在项目根目录下创建 `openspec/` 文件夹，标准结构如下：

```
openspec/
├── AGENTS.md           # AI 工作说明书（给 Cursor 等 AI 的约定与上下文）
├── project.md          # 项目介绍与约定（技术栈、命名、目录说明）
├── specs/              # 已实现的功能规范（按能力分目录）
└── changes/            # 待实施的变更提案（每个变更一个子目录）
```

### 3.2 规范目录（specs/）

按**能力（capability）**分文件组织，每个子目录描述一个独立的系统能力：

```
openspec/specs/
├── user-auth/
│   └── spec.md
├── payment-capture/
│   └── spec.md
└── [其他能力]/
    └── spec.md
```

### 3.3 变更目录（changes/）

每个变更提案一个子目录，遵循统一结构：

```
openspec/changes/[change-id]/
├── proposal.md         # 为什么、改什么、影响范围
├── tasks.md            # 实施任务清单（可勾选 - [ ] / - [x]）
├── design.md           # 技术决策（可选，仅在需要时创建）
└── specs/
    └── [capability]/
        └── spec.md     # 规范增量详情（ADDED/MODIFIED/REMOVED）
```

---

## 四、文件说明与规范要点

### 4.1 AGENTS.md

- **用途**：为 AI 助手提供项目类型、开发约定、关键路径。
- **建议内容**：项目类型、规范优先原则、变更 ID / 能力命名约定、与 `project.md` / `specs/` / `changes/` 的引用关系、与 AI 协作时的行为约定（如先引用规范、建议创建提案、按 tasks 推进、有待决议项或其他疑问时 AI 主动发问等）。
- **必须明确（见 1.2）**：可调用的 **`/ai-agent-dev-system/skills/`** 中的技能及触发词/路径；需要额外遵循的 **`/ai-agent-dev-system/global-rules/`** 中的全局规则。采用本规范配套 Skill 时，当用户指令匹配某技能的触发场景（如「功能验收」「代码评审」「分析需求」等）时，**须先读取该技能 SKILL.md 再按其中步骤执行**，避免跳过技能按常识执行；触发词与技能路径见 `/ai-agent-dev-system/global-rules/skills-rules-for-agent.md`。

### 4.2 project.md

- **用途**：项目介绍、架构模式、技术栈、目录结构、命名与格式约定，作为**本项目整体宪法规范**、顶层约定。
- **建议内容**：项目简介、技术栈与目录结构约定、change-id 与 capability 命名规则、规范增量书写格式说明、openspec 与业务代码的关系。
- **必须明确（见 1.2）**：额外需严格遵循的 **`/design/project-rules/`** 下的文档（作为工程宪法 project.md 的补充约束）。
- **与 `design/project-rules/` 的引用关系**：对技术实现、格式与流程的细化由 `design/project-rules/` 作为补充约束，与 project.md 共同构成完整约定体系，实现与评审时须同时遵守。

### 4.3 proposal.md（变更提案）

- **用途**：声明变更目标、范围、非目标、依赖与风险。
- **建议结构**：`## Why`（为什么）、`## What Changes`（改什么）、`## Impact`（影响范围，如 Affected specs、Affected code）、可选 `## Non-Goals`、`## Dependencies`、`## Risks`；**可选** `## 协同与技能`（本变更由哪些角色/Agent 按何种技能参与，需求分析产出存放于 `design/documents/[change-id]/` 的哪些文档，便于新项目与现有项目统一追溯）。

### 4.4 tasks.md（任务清单）

- **用途**：拆解为小步、可验证的工作项，便于实施与勾选。
- **格式**：使用 Markdown 任务列表 `- [ ]` / `- [x]`。
- **勾选时机与权责**：
  - **纯实现任务**（交付物为代码/文件，无「在…中验证」「确认…一致」等可验证行为）：实现完成（或经 code review）后可将对应项改为 `- [x]`。
  - **验证类任务**（任务描述中含「在…中验证」「确认…一致」等可验证行为）：须在 tasks.md 中标注**负责人**（如测试 Agent 或验收执行方）及**验收清单路径**（如 `design/documents/[change-id]/xxx-验证清单.md`）；**仅当验收通过后**方可将该任务勾选为 `- [x]`，且应由验收执行方或主 Agent 根据验收记录勾选，**不得由实现方在未经验收时单独勾选**。

### 4.5 design.md（可选）

- **何时创建**：仅在以下情况创建——
  - 跨多个服务/模块的变更
  - 新的架构模式
  - 新的外部依赖或重大数据模型变更
  - 安全、性能或迁移复杂性
  - 需要在编码前做技术决策的模糊点
- **结构与产出物质量**：由架构 Agent 执行 project-analysis 产出时，**最小结构**（变更目标与范围、架构与模块、接口与数据、关键流程与执行逻辑、异常/安全/性能、与需求/PRD 对应）与**自检**须符合 `ai-agent-dev-system/skills/project-analysis/REFERENCE/技术方案与架构产出物-最小结构与自检.md`。若存在**技术架构图、执行逻辑图、数据流图**等，可存放于 `design/documents/[change-id]/architecture/` 或 `design/project-rules/`，并在 design.md 中引用，便于实现与 code-review 按图核对。

### 4.6 specs/[capability]/spec.md（规范增量）

- **用途**：描述本变更对该能力的**增量**（新增、修改、移除），作为编码实现与功能验收（func-test）的**可执行依据**；与 `design/documents/[change-id]/` 下迭代需求说明或功能需求说明书（PRD）中的功能列表、验收标准、需求验收 Checklist 对应，便于从需求 → spec → 实现 → 验收 全链路追溯。
- **产出时机与技能**：spec 通常由执行 **request-analysis** 时在产出 `design/documents/[change-id]/` 下 PRD 后同步或随后产出；须符合 `ai-agent-dev-system/skills/request-analysis/REFERENCE/` 中新增类/修改类需求分析 spec 的约定（如 ADDED/MODIFIED/REMOVED、Requirements + Scenario 结构），并与 PRD 自检通过后再进入 tasks、编码与验收。
- **与 design/documents（PRD）的对应**：
  - spec 中的 **Requirements** 与 **Scenario** 应与 PRD 的「功能列表与验收标准」（REFERENCE 第 6 类）、「需求验收 Checklist」（第 7 类）可互相引用、无冲突；func-test 执行时对照 spec 与 design/documents 下验收 Checklist，产出验收记录。
  - **Scenario** 的编写可与 PRD 的「场景描述」「产品方案要点」（toC/toB 功能点）对齐；必要时在 spec 或 PRD 中注明引用关系（如「见 design/documents/[change-id]/迭代需求说明.md 5.1」「布局与交互见 design-assets/」）。
  - **capability** 的划分可与 PRD 的功能点或模块对应（如多语言、页头页脚、首页组装等），便于按能力追溯需求 → spec → 实现。
- **关键格式要求**：
  - 使用 `## ADDED Requirements`、`## MODIFIED Requirements`、`## REMOVED Requirements` 分段。
  - 每个需求至少包含一个 `#### Scenario:`（4 个 `#`）；Scenario 可包含 **WHEN / THEN** 或与 PRD 场景描述一致的步骤与预期。
  - 使用 `SHALL` / `MUST` 表示规范性需求。
  - **MODIFIED** 时须写出**完整**的修改后需求内容，而非片段增量。
- **REMOVED 建议**：注明 `**Reason**:`（为什么移除）、`**Migration**:`（如何迁移）。

**示例结构：**

```markdown
## ADDED Requirements
### Requirement: 新功能名称
系统必须（SHALL）提供...
#### Scenario: 成功场景
- **WHEN** 用户执行操作
- **THEN** 预期结果

## MODIFIED Requirements
### Requirement: 现有功能名称
[完整的修改后的需求，包含所有场景]

## REMOVED Requirements
### Requirement: 旧功能名称
**Reason**: 为什么移除
**Migration**: 如何处理迁移
```

---

## 五、命名规范

| 类型 | 规则 | 示例 |
|------|------|------|
| **change-id** | kebab-case，动词开头，唯一 | `add-user-profile`、`update-auth-flow`、`remove-old-api` |
| **capability** | 动词-名词，单一职责 | `user-auth`、`payment-capture`、`cart-drawer` |

- **简单优先**：默认单次变更 &lt; 100 行新代码；单文件实现直到证明不够用；避免不必要的框架。

### 5.1 保留的 change-id：项目前期（各项目通用）

**所有项目从一开始的所有任务，都必须归属于某一 change-id**，包括立项研究、需求分析等尚未进入研发迭代的阶段。

为此约定**保留的、各项目通用的 change-id**：

| 保留 change-id | 含义 | 适用阶段 | 主要执行方 | 目录与迭代日志 |
|----------------|------|----------|------------|----------------|
| **`project-early-phase`** | 项目前期，非研发迭代变更性质；供主 Agent、产品经理 Agent 开展立项研究、需求分析、市场研究、产品方案等早期工作 | 自项目启动至首个研发迭代变更创建之前 | 主 Agent、产品经理 Agent | **`design/documents/project-early-phase/`** 存放产出；调用记录统一追加到项目级 **`design/documents/迭代日志.md`** |

- **与一般 change-id 的区分**：`project-early-phase` 为**保留语义**，不受「动词开头」命名约束；不要求必须创建 `openspec/changes/project-early-phase/`（若项目希望为前期工作建 proposal/tasks 可自愿创建）。
- **何时切换**：一旦项目决定启动首个研发迭代变更（新建功能/迭代/小版本），则创建新的 change-id（如 `init-mvp`、`add-homepage` 等），按 6.1 先建 `design/documents/[change-id]/` 再建 `openspec/changes/[change-id]/`；此后的任务归属该变更，不再使用 `project-early-phase` 作为研发任务的 change-id。

---

## 六、变更启动顺序与检查清单

**总则**：**所有项目从一开始的所有任务，都必须有 change-id**。项目前期（立项研究、需求分析等）使用保留的 **`project-early-phase`**（见 5.1）；研发迭代变更使用自定的 change-id（见 6.1）。

以下规则适用于**新项目 0-1 的第一个变更**与**现有项目的任意新变更/迭代**。执行人或 AI 在创建变更时，**无须依赖项目内是否已存在 AGENTS.md 或 proposal.md**：以本规范（OpenSpec.md）为唯一依据，先阅读本节再创建目录与文档。

### 6.1 变更启动顺序（强制）

凡新建变更（含新功能、迭代、小版本），须按以下顺序执行：

1. **先**在项目内 `design/documents/` 下创建子目录 **`design/documents/[change-id]/`**，并存放**至少一份**需求侧产出（如《迭代需求说明》《功能需求说明书》《需求验收 Checklist》或《市场研究与产品方案》等）；可由产品经理或执行 request-analysis 技能时产出（先读 `ai-agent-dev-system/skills/request-analysis/SKILL.md`）。
2. **再**在 `openspec/changes/` 下创建 **`openspec/changes/[change-id]/`** 及 proposal.md、tasks.md、可选 design.md、specs/；proposal.md 中须**引用**上述 design/documents 路径或文档名，建立可追溯关系。

**简化例外**：极小范围热修可在 proposal 中声明「本变更为极小范围热修，已合并需求于 proposal，design/documents 仅保留 README」，并仍建议保留 `design/documents/[change-id]/README.md` 以保持可追溯。

### 6.2 变更启动检查清单（新建变更或迭代时必过）

在创建或开始实施变更前，自检以下 5 条（不依赖项目内 AGENTS.md 是否存在，以本规范为准）：

1. 已创建 **`design/documents/[change-id]/`** 并存放至少一份需求/验收文档（产品经理或 request-analysis 产出）。
2. 已创建 **`openspec/changes/[change-id]/`** 且 **proposal.md** 中引用上述 design/documents 路径或文档名。
3. **tasks.md** 中任务已按能力拆分，并建议标注**负责人**（对应子 Agent）；凡任务描述中含「在…中验证」「确认…一致」等**可验证行为**的，**必须**标注负责人（如测试 Agent）及验收清单路径（或引用 design/documents 下验证清单），且仅验收通过后方可勾选该任务。执行时由主 Agent 拆任务给该负责人，**被指派的执行方**按 **`ai-agent-dev-system/global-rules/skills-rules-for-agent.md`** 中**本 Agent 角色**的「主导/联动技能」先读取该技能 SKILL.md 再按步骤执行（技能由执行方角色 + skills-rules 决定，不按任务类型反推）。
4. 编码实现前，执行方已读取 `design/documents/[change-id]/` 与 `openspec/changes/[change-id]/` 下相关文档；执行方按 skills-rules 中本角色对应技能，须先读 `ai-agent-dev-system/skills/<技能名>/SKILL.md` 再执行。
5. **迭代日志（强制）**：已创建或约定首次调用时创建项目级迭代日志文档 **`design/documents/迭代日志.md`**；且**每次**在该变更上下文中调用 Agent 或技能时**须在产出完成后追加一条**记录，并在记录中明确写出当前 `change-id`，格式见 **`projects-rules-for-agent.md`**「Agent 与技能调用迭代日志」。主 Agent 在验收或归档前可核对该项目级迭代日志是否与调用一致。

### 6.3 新项目 0-1 的适用说明

- **项目一开始**：自项目启动起，**所有任务均须有 change-id**。若项目尚未有 `openspec/`，则按本规范第一节「新项目第一件事」先创建 `openspec/` 并填写 AGENTS.md、project.md。
- **项目前期（立项研究、需求分析等）**：使用保留的 change-id **`project-early-phase`**（见 5.1）。**必须**在首次进行项目前期工作时创建 **`design/documents/project-early-phase/`**，并在项目级 **`design/documents/迭代日志.md`** 中记录该 change-id 下的每次 Agent/技能调用，格式见 **`projects-rules-for-agent.md`** 第三节。主 Agent、产品经理 Agent 开展早期工作均归属此 change-id；**不要求**创建 `openspec/changes/project-early-phase/`（项目可自愿创建）。
- **首个研发变更**：当项目决定启动首个研发迭代变更时，新建自定 change-id（如 `init-mvp`），仍须先建 `design/documents/[change-id]/` 并放入需求侧文档，再建 `openspec/changes/[change-id]/`，不因「第一个变更」而跳过顺序。
- **proposal 模板**：首个 proposal 与后续所有 proposal 均按本规范 4.3 节建议结构（含可选「协同与技能」）编写，无需已有 proposal 作为拷贝来源。

### 6.4 规则加载与「用户一发起需求就触发」的前提

本节（变更启动顺序与检查清单）与「OpenSpec 变更入口」（在 `ai-agent-dev-system/global-rules/projects-rules-for-agent.md` 中）只有在**当前宿主已成功加载治理规则**时才会生效。不同宿主的加载方式不同，无法保证任意环境下都能在对话一开始 100% 自动加载 `projects-rules-for-agent.md`。

为尽量做到「用户一发起新需求/新建变更就触发先读本节与 4.3 节再执行」，建议：

1. **工作区 / 规则来源**：确保 `ai-agent-dev-system` 或其导出的治理规则文件可被当前宿主访问，并已被配置为规则来源。
2. **宿主入口文件**：在对应宿主的入口文件中增加一条：“当用户提出新功能、新建变更、迭代、出方案等时，先读取 OpenSpec.md 第六节与 4.3 节，再按该节执行。”
3. **项目内双保险**：在每个采用 OpenSpec 的项目根目录中放置当前宿主可识别的最薄入口文件，要求 Agent 在处理新需求 / 新变更前先读取 `ai-agent-dev-system/OpenSpec.md` 第六节与 4.3 节，再按变更启动顺序执行。
4. **宿主差异化说明**：具体到 Cursor / VS Code / 第三方插件的加载方式，分别见 `platform-adapters/cursor/`、`platform-adapters/vscode/`、`platform-adapters/generic/`。

---

## 七、三阶段工作流

### 阶段 1：创建变更提案（Planning）

- **何时创建提案**：添加新功能；破坏性变更（API、数据库 schema）；架构或模式变更；性能优化（改变行为）；安全模式更新。
- **何时跳过提案**：Bug 修复（恢复预期行为）；拼写、格式、注释；非破坏性依赖更新；配置变更；现有行为的测试。
- **步骤**（须符合第六节「变更启动顺序与检查清单」）：查看现有 `specs/` 与进行中的 `changes/` → 选定唯一 change-id → **先**创建 `design/documents/[change-id]/` 并存放至少一份需求/验收文档 → **再**创建 `openspec/changes/[change-id]/` 及 `specs/[capability]/` → 编写 `proposal.md`（可含「协同与技能」）、`tasks.md`、可选 `design.md`、`specs/[capability]/spec.md` → proposal 中引用 design/documents 路径 → 使用 `openspec validate` 校验。

### 阶段 2：实施变更（Implementation）

- **实施前**：阅读 `proposal.md`、`design.md`（如有）、`tasks.md`、相关 `spec.md`、`project.md`。
- **实施中**：按 `tasks.md` 顺序完成任务，完成后将 `- [ ]` 改为 `- [x]`。
- **注意**：提案被审核批准前不建议开始实施。

### 阶段 3：归档变更（Archiving）

- **部署后**：使用 `openspec archive <change-id> --yes` 归档，工具会更新 `specs/`。
- **仅归档不更新 specs**：`openspec archive <change-id> --skip-specs --yes`（适用于工具类变更）。
- **验证**：`openspec validate --strict`。

---

## 八、常用命令速查（需安装 OpenSpec CLI）

```bash
openspec list              # 列出进行中的变更
openspec list --specs      # 列出所有规范
openspec show [item]       # 查看变更或规范详情
openspec validate [item]   # 验证变更或规范
openspec validate --strict # 严格模式验证
openspec archive <id> --yes          # 归档变更（更新 specs）
openspec archive <id> --skip-specs --yes  # 仅归档，不更新 specs
openspec show [change] --json --deltas-only  # 查看增量详情（调试）
```

---

## 九、常见问题排查

- **"Change must have at least one delta"**：检查 `changes/[name]/specs/` 下是否存在 `.md` 文件，且包含 `## ADDED Requirements`（或 MODIFIED/REMOVED）前缀。
- **"Requirement must have at least one scenario"**：确认使用 `#### Scenario:`（4 个 `#`），勿用项目符号或粗体作为场景标题。
- **验证失败**：使用 `--strict` 模式，或 `openspec show [change] --json` 查看结构。

---

## 十、多项目复用建议

1. **新项目（第一件事）**：在项目根目录创建 `openspec/`，**严格遵循本规范（OpenSpec.md）** 复制目录结构；根据 openspec 规范与项目类型填写 `AGENTS.md` 与 `project.md`。填写时优先引用 `openspec/` 下规范与提案，并严格遵循 OpenSpec.md；AGENTS.md 须明确可调用的 `ai-agent-dev-system/skills/` 与需遵循的 `ai-agent-dev-system/global-rules/`，project.md 须明确需遵循的 `design/project-rules/`（见第一节 1.2）。
2. **现有项目**：在不影响现有代码的前提下新增 `openspec/`，填写 `AGENTS.md`（项目类型、可调用的技能与需遵循的全局规则、关键路径等，见 1.2）与 `project.md`（说明与技术栈、目录的对应关系及需遵循的 `design/project-rules/`）。
3. **与 AI 协作**：将本文件或 `openspec/AGENTS.md` 作为规则或上下文，使 AI 优先引用 `openspec/` 下的规范与提案，并在建议新功能时提示是否需创建 OpenSpec 变更提案。

---

*文档版本：基于 OpenSpec 使用指南与社区实践整理，适用于长期、多项目复用。*
