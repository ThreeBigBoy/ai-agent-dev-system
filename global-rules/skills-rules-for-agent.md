---
description: OpenSpec 补充 - Agents（agents/）与 Skills（skills/）赋能对应关系，以及各 Skill 的应用关系与触发约定，复用于所有项目
alwaysApply: true
---

# Agents 与 Skills 的应用关系

本规则为**驱动所有项目开发的补充规范**，作为 `OpenSpec.md` 的补充，**复用于所有项目**。

为便于在 Cursor / AI 协作场景下复用本规范，建议将以下 Skill 作为 OpenSpec 的标准配套。

**技能触发约定**：当用户指令匹配某技能的触发场景时，执行方（由 **`agents/`** 下角色与本节「Agents 与 Skills 赋能对应关系」表确定）须**先读取 `ai-agent-dev-system/skills/` 下该技能目录的 SKILL.md**，再按其中步骤执行；否则易出现「按常识执行、产出物不符合技能约定」等问题。采用本规范的项目应在 `openspec/AGENTS.md` 中为**所有有主导/联动技能的 Agent** 列出触发词与技能路径（见本节「项目 openspec/AGENTS.md 建议」），便于 AI 一致遵守。

**执行后必做收尾（通用，所有技能均适用）**：在某一 **change-id** 上下文中执行**任意**技能并产出后，执行方**必须在本轮对话内、向用户作出完成性/交付性回复之前**，向项目级 **`design/documents/迭代日志.md`** **追加一条**记录，并在记录中明确写出当前 `change-id`，格式见 **`projects-rules-for-agent.md`**「Agent 与技能调用迭代日志」（含使用模型）；文件不存在则新建。未完成不得视为该次任务完成；作出完成性/交付性回复前须自检，未追加则**先追加再**回复。无明确 change-id 时可跳过。

**运行后端说明（V2.1）**：当项目选择某个运行时后端（如 `agent_team_project`）承接默认执行链路时，该后端属于**执行实现**而非**治理权威源**。角色边界、技能映射、日志与验收要求仍以 OpenSpec、`projects-rules-for-agent.md` 与本文件为准。

---

## Agents 与 Skills 赋能对应关系

以下对应关系与 `agents/` 中的 Agent 角色一致。**主 Agent** 统筹任务拆解并监督各子 Agent 按本表正确触发技能；子 Agent 执行技能时须**先读取对应技能目录下的 SKILL.md**，再按步骤执行，确保产出符合 OpenSpec 规范。

| Agent（agents/） | 主导/赋能技能（skills/） | 联动或可选技能 | 说明 |
|------------------------------|--------------------------|----------------|------|
| **主 Agent** | — | 全链路协调 | 不直接执行某一技能；统筹 request-analysis → project-analysis → coding-implement → code-review → func-test 全链路，监督各 Agent 按本表触发技能，确保规范落地。完整质量闭环为 **10 步**（含验收后 **归档 → 复盘 → 全局检查**），见 `memory/patterns/pattern-complete-quality-closed-loop.md`。 |
| **产品经理 Agent** | request-analysis | image-analysis | 主导需求分析、变更提案与 specs 编写；需求涉及前端或含设计图/截图时联动 image-analysis，解析结果纳入需求与 spec。 |
| **架构 Agent** | project-analysis、code-review | — | 主导工程结构分析（project.md、design/project-rules/）、OpenSpec CLI 与代码评审；产出技术规范与评审报告，推动规范与实现一致。 |
| **前端 Agent** | coding-implement（前端） | image-analysis | 按 specs 与 project 约定实现前端代码；引用 image-analysis 的解析结果做 UI/设计图还原与场景描述落地。 |
| **后端 Agent** | coding-implement（后端） | — | 按 specs 与 project 约定实现接口、逻辑与数据层；配合 info-database、info-service-interface 等元信息文档。 |
| **测试 Agent** | func-test | — | 主导功能测试与验收，对照 Requirements + Scenarios 与验收 Checklist 执行测试，产出验收记录并推动问题闭环。 |
| **文档 Agent** | — | request-analysis、project-analysis | 无单独技能；维护 README、接口文档、AGENTS.md、project.md 等，配合需求与工程分析产出规范文档，与 openspec/ 及 design/ 保持一致。 |
| **Bug 修复 Agent** | — | code-review、func-test | 无单独技能；负责根因分析、最小改动修复与验证；可配合 code-review 与 func-test 做问题确认与回归验证。 |

**使用说明**：主 Agent 分配任务时，应依据上表将「需求分析」「工程结构分析」「编码实现」「代码评审」「功能验收」等任务指派给对应 Agent，并注明需触发的技能路径（如 `ai-agent-dev-system/skills/request-analysis/`）；被指派的 Agent 须先加载该技能 SKILL.md 再执行，避免越权执行或产出物不符合技能约定。

---

## 项目 openspec/AGENTS.md 建议（通用）

采用本规范的项目应在 **`openspec/AGENTS.md`** 中，按本节「Agents 与 Skills 赋能对应关系」表，为 **`ai-agent-dev-system/agents/`** 下**所有有主导或联动技能的 Agent** 列出**触发词**与**技能路径**，便于主 Agent 与人类一致地指派任务并触发对应技能。

- **技能路径**：指向 **`ai-agent-dev-system/skills/[技能目录名]/`** 下 **SKILL.md**（以实际仓库中规范与技能存放位置为准）；表中所列技能目录与 `ai-agent-dev-system/skills/` 下各技能一一对应（如 request-analysis、project-analysis、coding-implement、code-review、func-test、image-analysis 等）。
- **填写方式**：可依上表逐行填写——每个 Agent 的触发词示例（如「需求分析」「补充 PRD」「代码评审」「功能验收」等）及该 Agent 主导/联动技能路径；确保 **agents 下所有角色** 与 **skills 下所有被引用的技能** 均被覆盖，避免漏指派或漏读 SKILL。
- **用户提示**：若用户在任务中**明确指定执行方**（如「由产品经理 Agent 执行」「让架构做评审」）或**明确指定技能**（如「先读 request-analysis 的 SKILL」），须遵从用户指定；未指定时，按 `projects-rules-for-agent.md` 中「任务类型与执行方、技能对应」及本表推断执行方与技能，执行方须先读取对应 SKILL.md 再执行。

---

### 9.1 request-analysis（需求分析）

当项目采用 OpenSpec 且需要进行**需求分析**时，可加载 **request-analysis** 技能，使产出与本规范对齐。

- **技能路径**（示例）：`ai-agent-dev-system/skills/request-analysis/`（以实际仓库中规范与技能存放位置为准）。
- **触发场景**：用户输入「分析需求」「需求分析」或提供功能描述/业务目标，希望得到结构化方案、项目前期文档与变更提案时。
- **技能产出（示例流程）**：
  1. 为本次需求确定或复用 `change-id`，在 `design/documents/[change-id]/` 下创建本次需求的子目录，并在其中编写**市场研究与产品方案**、**功能需求说明书**、**需求验收 Checklist** 等项目前期方案文档。
  2. 若项目根目录不存在 `openspec/` 或缺少 `openspec/AGENTS.md` / `openspec/project.md`，则按本规范初始化 `openspec/` 目录结构与 AGENTS、project 等项目宪法文件；若已存在则对照本次需求判断是否需要适度更新。
  3. 识别本次需求为**新增类**或**修改类**，并在 `openspec/changes/[change-id]/` 下创建或更新需求变更目录：产出 `proposal.md`、`tasks.md`、可选 `design.md` 以及 `specs/[capability]/spec.md` 结构化需求分析文档（ADDED / MODIFIED / REMOVED Requirements + Scenario）。
  4. 任务拆分遵循该技能 REFERENCE 中的「任务拆分 spec」，输出可勾选任务列表至 `tasks.md`。
  5. **records/ 归类**：以「反思-」「复盘-」「对齐结论」、「XX验收记录」、「XX测试记录」等命名的过程反思、复盘、对齐结论及验收/测试记录类文档应置于 **`design/documents/[change-id]/records/`**，与功能验收/代码评审记录一起便于按变更聚合与归档（与 OpenSpec 1.1 表一致）。
  6. **迭代日志（强制，执行后必做收尾）**：每次在本变更上下文中调用 `agents/` 下 Agent 或 `skills/` 下技能时，**必须在本轮对话内、任务闭环前**在项目级 **`design/documents/迭代日志.md`** 中**追加**一条记录，并在记录中明确写出当前 `change-id`，格式见 **`projects-rules-for-agent.md`**「Agent 与技能调用迭代日志」（含使用模型）；文件不存在则新建。**未完成不得视为该次任务完成**。本约定为主 Agent 及所有子 Agent 的必做收尾动作，适用于所有采用 OpenSpec 的项目与所有迭代/变更。
- **联动**：若需求涉及前端或含设计图/截图，可同时加载 **image-analysis** 技能解析图片，将解析结果纳入需求说明与 spec 中的场景描述。

将本规范与 request-analysis 技能配合使用，可在「分析需求」场景下自动产出符合 OpenSpec 的文档与变更结构，便于后续实施与归档。

### 9.2 project-analysis（工程结构分析）

当需要**分析工程结构或技术实现方案**，并确保变更与当前架构/技术栈/目录结构兼容时，可加载 **project-analysis** 技能。

- **技能路径**（示例）：`ai-agent-dev-system/skills/project-analysis/`。
- **触发场景**：
  - 用户输入「分析工程结构」「分析技术实现方案」；
  - 或在变更提案阶段，用户希望检查「本次需求是否需要调整架构/技术栈/目录结构」。
- **核心职责**：
  1. 结合 `request-analysis` 输出（如 `documents/` 与 `openspec/changes/[change-id]/` 下的 `proposal.md`、`design.md`、`specs/*`），判断本次需求对工程结构的影响范围。
  2. 按本规范审视或初始化 `openspec/project.md`，将项目定位、开发环境、架构模式、技术栈、目录结构、命名与格式等作为**项目宪法规范**固化；若已存在且本次需求无重大结构变化，则可跳过更新。
  3. 深入调研与当前工程强相关的开发环境与平台生态官方文档，检查或补充 `design/project-rules/` 下的核心名词概念、产品/数据模型、关键信息流/数据流与实现约束等；若原有内容完备且本次需求不构成结构性变化，则可跳过更新。
  4. 将结构分析结论反馈到当前变更目录 `openspec/changes/[change-id]/`，在 `proposal.md` / `design.md` / `specs/*` 中补充或修订与工程结构相关的说明与 Requirements + Scenarios；**技术方案（design.md）与架构图等产出物**须符合 project-analysis 技能 **REFERENCE**《技术方案与架构产出物-最小结构与自检》中的最小结构与自检清单（路径：`ai-agent-dev-system/skills/project-analysis/REFERENCE/`）。
- **协同关系**：
  - 与 `request-analysis`：通常先由 `request-analysis` 完成需求与场景分析，再由 `project-analysis` 从工程与架构视角校准 `project.md`、`design/project-rules/` 及对应变更文档。
  - 与 `image-analysis`（可选）：当用户提供架构图、数据流图等图片时，可先由 `image-analysis` 解析，再由本技能将结果结构化写入 `project.md`、`design/project-rules/` 与相关 `specs/*`。

通过将本规范与 request-analysis、project-analysis 等技能协同使用，可在「分析需求 → 分析工程结构 → 形成变更提案与规范增量」的完整链路中，自动产出符合 OpenSpec 的文档与变更结构，便于后续实施与归档。

### 9.3 coding-implement（编码实现）

当进入**编码实现阶段**，希望根据既有需求与工程结构文档自动生成或修改代码，并同步管理数据库与接口元信息文档时，可加载 **coding-implement** 技能。

- **技能路径**（示例）：`ai-agent-dev-system/skills/coding-implement/`。
- **触发场景**：
  - 用户输入「编码实现」「根据这个 change 开始写代码」等；
  - 或在完成需求分析与工程结构分析后，希望 AI 按既定规范生成前后端代码。
- **核心职责**：
  1. 以单一 `change-id` 为工作单位，读取 `design/documents/[change-id]/` 及 `openspec/changes/[change-id]/proposal.md`、`design.md`、`specs/*/spec.md`，并结合 `openspec/project.md` 与 `design/project-rules/`，锁定本次实现的范围与规范约束。
  2. 根据编码内容类型，选择 `coding-implement/REFERENCE/` 下的相应规范（如前端 `spec-frontend.md`，后端 `spec-backend-*.md`），并据此在项目代码目录中创建或修改符合分层与命名约定的代码文件。
  3. 若本次变更涉及**新增或调整数据库表结构**，在项目根目录下维护 `info-database/`（如表结构说明与 DDL 脚本）；若涉及**新增或调整对外服务接口**，在项目根目录下维护 `info-service-interface/`（接口说明文档），确保与数据模型和接口规范一致。
  4. 实施完成后，回到 `openspec/changes/[change-id]/tasks.md` 更新任务状态，并在需要时补充实现相关的关键设计说明；**实现完成后**须按 coding-implement 技能 **REFERENCE**《实现完成自检》执行自检（路径：`ai-agent-dev-system/skills/coding-implement/REFERENCE/实现完成自检.md`），通过后再进入 code-review 或 func-test。
- **协同关系**：
  - 与 `request-analysis`：其输出提供需求与变更结构化文档与任务拆分，是编码实现的前置条件。
  - 与 `project-analysis`：其输出提供最新的项目宪法规范与工程补充约束，编码必须遵守；如实现中发现结构与实现不一致，应提示回到结构分析阶段修正。

通过将本规范与 request-analysis、project-analysis、coding-implement 协同使用，可打通「分析需求 → 分析工程结构 → 编码实现」的完整闭环，使生成代码长期与 OpenSpec 文档与工程约定保持一致。

### 9.4 code-review（代码评审）

当需要对**已有或刚完成的实现**进行系统化 Code Review，并将结果与 OpenSpec 文档和任务体系打通时，可加载 **code-review** 技能。

- **技能路径**（示例）：`ai-agent-dev-system/skills/code-review/`。
- **触发场景**：
  - 用户输入「编码实现后做代码评审」「对这个 change 做 code review」等；
  - 或在合并/发布前，希望对某个 `change-id` 进行质量把关并形成记录。
- **核心职责**：
  1. 以前置技能 `request-analysis`、`project-analysis`、`coding-implement` 的输出为基础，读取 `design/` 与 `openspec/changes/[change-id]/` 下文档与代码改动，对本次变更进行多维度 Review（需求符合性、架构分层、代码质量、安全/性能、日志与监控、测试等）。
  2. 参考 `code-review/REFERENCE/` 下的通用 review 规范与 OpenSpec 集成规范，在 **`design/documents/[change-id]/records/`** 下输出结构化的评审记录，建议文件名 **`[change-id]-code-review.md`**（包含问题清单与后续行动）；**最小结构与自检**须符合 code-review 技能 **REFERENCE**《评审报告-最小结构与自检》（路径：`ai-agent-dev-system/skills/code-review/REFERENCE/`）。
  3. 对 Blocking/Major 级问题，将修复工作转化为 `openspec/changes/[change-id]/tasks.md` 中的任务项，并在问题关闭后勾选完成；如发现需新变更提案或规范调整的内容，则建议创建新的 change-id 或更新相关规范文档。
- **协同关系**：
  - 与 `coding-implement`：形成「实现 → 评审 → 迭代」闭环；评审建议可作为下一轮实现的输入。
  - 与 `request-analysis`、`project-analysis`：在 Review 中发现的需求/架构层问题，可回溯到对应变更或规范进行修订，并在评审记录中说明原因。

### 9.5 func-test（功能测试与验收）

当进入**功能测试/验收阶段**，希望根据 OpenSpec 中的 Requirements + Scenarios 与验收 Checklist，对实现进行系统化验证并形成记录时，可加载 **func-test** 技能。

- **技能路径**（示例）：`ai-agent-dev-system/skills/func-test/`。
- **触发场景**：
  - 用户输入「功能验收」「功能测试」等；
  - 或在编码与代码评审完成后，希望对某个 `change-id` 进行功能级验收。
- **核心职责**：
  1. 以前置技能 `request-analysis`、`project-analysis`、`coding-implement`（以及可选的 `code-review`）的输出为基础，围绕指定 `change-id` 整理测试范围与用例，对照 `specs/*/spec.md` 的 Requirements + Scenarios 与 `需求验收Checklist` 执行功能测试。
  2. **OpenSpec 本身需包含的操作**：第一轮执行 `openspec validate [change-id]`，验证已开发代码的变更需求与文档一致性；第二轮在执行完测试并输出验收记录后执行 `openspec validate --strict`，严格模式验证通过后再给出是否推荐通过本次验收的结论；两轮结果记入验收记录。
  3. 参考 `func-test/REFERENCE/` 下的通用功能测试与 OpenSpec 集成规范，在 **`design/documents/[change-id]/records/`** 下输出结构化的验收记录，建议文件名 **`[change-id]-func-test.md`**（或 `-acceptance.md`）；**最小结构与自检**须符合 func-test 技能 **REFERENCE**《验收记录-最小结构与自检》（路径：`ai-agent-dev-system/skills/func-test/REFERENCE/`），两轮 validate 结果须记入记录。
  4. 将测试中发现的关键问题转化为 `openspec/changes/[change-id]/tasks.md` 中的任务，并在问题修复与重测后更新记录与任务状态；如涉及需求或架构层调整，则建议通过新的 change-id 或规范更新进行处理。
- **协同关系**：
  - 与 `coding-implement`、`code-review`：形成「实现 → 评审 → 功能验收」的质量闭环。
  - 与 `request-analysis`、`project-analysis`：确保功能测试严格对齐需求与架构约定，测试中发现的需求/结构问题会反向推动文档与规范的修订。

### 9.6 image-analysis（图片分析）

当**需求涉及前端或用户提供了设计图/原型图/截图/架构图**等图片，需要将视觉信息转化为结构化描述并纳入需求与 spec 时，可加载 **image-analysis** 技能。

- **技能路径**（示例）：`ai-agent-dev-system/skills/image-analysis/`。
- **触发场景**：
  - **自动联动**：在「需求分析」环节，若需求涉及前端或含设计图/截图，由 request-analysis 自动加载本技能；
  - **显式触发**：用户输入「解析这张图」「根据截图写需求」「分析架构图」等。
- **核心职责**：
  1. 以前置技能 request-analysis、project-analysis 已产出或即将产出的 design/、openspec/ 文档为上下文，聚焦本次需求范围（按 `change-id` 识别）；若有图片，则按 `image-analysis/REFERENCE/` 中的图片分析规范进行解析。
  2. 将解析结果纳入需求说明与 spec 中的场景描述：写入 `design/documents/[change-id]/` 下功能需求说明书等文档，以及 `openspec/changes/[change-id]/specs/[capability]/spec.md` 中相关 Requirement 的 Scenario（布局、组件、文案、状态、交互等）；若为架构/数据流图，则写入 `design/project-rules/` 或对应 change 的 `design.md`。
  3. 在文档中标注解析来源与不确定性（如「需业务/设计确认」），保证可追溯与可验收。
- **协同关系**：
  - 与 `request-analysis`：需求分析涉及前端或含图片时，request-analysis 调用本技能解析图片，并将结果纳入 design/documents 与 openspec/changes 下的需求与 spec。
  - 与 `project-analysis`：用户提供架构图、数据流图时，可先经本技能解析，再由 project-analysis 将结果结构化写入 project.md、design/project-rules/。
  - 与 `coding-implement`：前端实现时可引用已写入需求与 spec 的图片解析结论，作为实现与验收依据。

### 9.7 prd-review（PRD 评审）

当需要对已产出的 **PRD（产品需求文档）** 进行系统化质量检查、完整性校验、逻辑审查，并在进入 proposal/tasks/specs 阶段前确保 PRD 达到「可商业化、可技术落地、可验收、可衡量」标准时，可加载 **prd-review** 技能。

- **技能路径**（示例）：`ai-agent-dev-system/skills/prd-review/`。
- **触发场景**：
  - 用户输入「评审 PRD」「检查 PRD 质量」「PRD 自检」「审查需求文档」等；
  - 用户需要在进入 proposal/tasks/specs 阶段前，确保 PRD 质量达标；
  - 用户需要回溯补录 PRD 评审纪要（基于历史对话和已产出文档）。
- **核心职责**：
  1. **加载规范**：首先读取 `skills/request-analysis/REFERENCE/迭代需求说明-PRD最小结构与自检.md`，确保评审标准统一。
  2. **系统化评审**：按照 REFERENCE 中的「三、自检清单」（9 项自检项）逐项评审 PRD，覆盖价值分析、竞品调研、迭代目标、产品方案、异常边界、文档命名规范等维度。
  3. **详细留痕**：在 `design/documents/[change-id]/records/` 下产出结构化的**评审纪要文档**，命名推荐 `PRD-[change-id]-评审纪要.md`，必须包含评审基本信息、评审过程记录（逐项自检的详细记录）、问题发现与处理、整体评审结论、附录。
  4. **形成判定**：对每项自检项给出判定（✓ 通过 / △ 有条件通过 / ✗ 不通过），并给出综合判定和后续行动建议。
- **协同关系**：
  - 与 `request-analysis`：request-analysis 产出 PRD，prd-review 对 PRD 进行质量把关，形成「产出 → 评审 → 完善」闭环。
  - 与 `project-analysis`：PRD 评审通过后，方可进入工程结构分析阶段；如 PRD 评审发现问题涉及架构可行性，可提前介入讨论。
  - 与 `architecture-review`：PRD 评审关注「需求真实性、产品方案完整性」，技术方案评审关注「架构合理性、实现可行性」，两者形成「需求 → 技术」的质量双保险。
- **产出物质量约定**：评审纪要须符合 `skills/prd-review/REFERENCE/PRD评审纪要规范.md` 中的内容结构、判定标准、输出格式；评审维度须围绕「价值层、执行层」两个底层逻辑展开。

### 9.8 architecture-review（技术方案评审）

当需要对已产出的 **技术方案（design.md）** 进行系统化架构合理性审查、可实现性评估，并在进入 coding-implement 阶段前确保技术方案达到「可被前端/后端按图实现、可被 code-review/func-test 对照验证」标准时，可加载 **architecture-review** 技能。

- **技能路径**（示例）：`ai-agent-dev-system/skills/architecture-review/`。
- **触发场景**：
  - 用户输入「评审技术方案」「检查架构设计」「技术方案自检」「审查 design.md」等；
  - 用户需要在进入 coding-implement 阶段前，确保技术方案质量达标；
  - 用户需要回溯补录技术方案评审纪要（基于历史对话和已产出文档）。
- **核心职责**：
  1. **加载规范**：首先读取 `skills/project-analysis/REFERENCE/技术方案与架构产出物-最小结构与自检.md`，确保评审标准统一。
  2. **系统化评审**：按照 REFERENCE 中的「三、自检清单」（9 项自检项）逐项评审技术方案，覆盖变更目标、架构一致性、需求可追溯性、接口与数据、关键流程、异常边界、文档命名规范等维度。
  3. **对照 PRD**：评审技术方案时必须对照 PRD，确保 100% 满足需求、无遗漏无冲突。
  4. **详细留痕**：在 `design/documents/[change-id]/records/` 或 `openspec/changes/[change-id]/` 下产出结构化的**评审纪要文档**，命名推荐 `技术方案-[change-id]-评审纪要.md`，必须包含评审基本信息、评审过程记录（逐项自检的详细记录）、问题发现与处理、整体评审结论、附录。
  5. **形成判定**：对每项自检项给出判定（✓ 通过 / △ 有条件通过 / ✗ 不通过），并给出综合判定和后续行动建议。
- **协同关系**：
  - 与 `project-analysis`：project-analysis 产出技术方案，architecture-review 对技术方案进行质量把关，形成「产出 → 评审 → 完善」闭环。
  - 与 `prd-review`：PRD 评审关注「需求真实性、产品方案完整性」，技术方案评审关注「架构合理性、实现可行性」，两者形成「需求 → 技术」的质量双保险。
  - 与 `coding-implement`：技术方案评审通过后，方可进入编码实现阶段；评审纪要可作为 coding-implement 的输入约束。
- **产出物质量约定**：评审纪要须符合 `skills/architecture-review/REFERENCE/技术方案评审纪要规范.md` 中的内容结构、判定标准、输出格式；评审维度须围绕「架构层、实现层、落地层」三个底层逻辑展开。

### 9.9 retrospective-analysis（复盘分析）

当需要对已完成的工作进行**系统化复盘**，将经验转化为可复用的知识资产时，可加载 **retrospective-analysis** 技能。

- **技能路径**（示例）：`ai-agent-dev-system/skills/retrospective-analysis/`。
- **触发场景**：
  - 用户输入「复盘」「总结」「回顾」「反思」等关键词；
  - 完成一个重要阶段/里程碑/项目后；
  - 问题反复出现时（提示进行复盘）；
  - 定期复盘（如每周/每月/每季度）。
- **执行方**：
  - 技术问题复盘：架构 Agent / 主 Agent
  - 产品需求复盘：产品经理 Agent / 主 Agent
  - 项目整体复盘：主 Agent
- **核心职责**：
  1. **执行 5 阶段复盘法**：
     - Stage 1: Review Goals（回顾目标）- 回顾初始目标和预期结果
     - Stage 2: Evaluate Results（评估结果）- 对比实际 vs 预期，识别亮点和问题
     - Stage 3: Analyze Causes（分析原因）- 5 个 Why 找到根本原因，思维模式分析
     - Stage 4: Extract Learnings（提炼经验）- 提炼可复用模式、识别反模式、提出改进建议
     - Stage 5: Action Plan（行动计划）- 制定短期/中期/长期行动计划
  2. **产出复盘报告**：按模板产出结构化的复盘报告，包含 8 章节（复盘背景、回顾目标、评估结果、分析原因、提炼经验、行动计划、关键洞察、附录）。
  3. **沉淀 Memory**：评估复盘成果是否值得沉淀为 memory（pattern、anti-pattern、preference、playbook、reflection），并创建相关 memory 文档。
  4. **更新迭代日志**：向迭代日志追加复盘记录。
- **协同关系**：
  - 与所有前置技能：复盘需要回顾 request-analysis → prd-review → project-analysis → architecture-review → coding-implement → code-review → func-test 全过程，以及验收后的**归档**与 **Step 10 全局检查**（10 步质量闭环 v1.3）。
  - 与 `pattern-five-stage-retrospective`：本技能是 5 阶段复盘法的具体执行实现。
  - 与 `pattern-breakthrough-thinking-redefine-problem-space`：复盘时分析思维模式差异（如 AI vs 用户）。
- **产出物质量约定**：
  - 复盘报告须符合 `skills/retrospective-analysis/REFERENCE/复盘报告模板.md` 中的 8 章节结构；
  - 质量门禁：通过「复盘质量自检（9 项）」检查（目标回顾、结果对比、问题识别、根因分析、思维模式分析、经验提炼、行动计划、memory 沉淀、文档规范）；
  - 评审判定：7 项及以上通过为通过，5-6 项通过为有条件通过，少于 5 项通过或有未通过项为不通过。

---

## 十、执行前查阅规范机制（v1.2 新增）

为防止**术语定义漂移**和**惯性思维陷阱**，确保每次执行技能时都按最新规范执行，特建立「执行前查阅规范」强制机制。

### 10.1 查阅要求

**执行任何技能前，必须完成以下查阅步骤**：

| # | 查阅项 | 查阅内容 | 目的 |
|---|--------|---------|------|
| C.1 | Skill 版本确认 | 确认使用的 skill SKILL.md 为最新版本 | 防止使用旧版本规范 |
| C.2 | 术语定义查阅 | 查阅本技能涉及的关键术语定义 | 防止术语定义漂移 |
| C.3 | 关联 Memory 唤醒 | 唤醒相关的 pattern/anti-pattern/preference | 获取最佳实践和避坑指南 |
| C.4 | 质量门禁检查清单 | 查阅本阶段的质量门禁检查清单 | 明确准出标准 |

### 10.2 查阅流程

```
用户指令触发技能执行
    ↓
执行前查阅规范（强制）
    ├── C.1 确认 skill 版本（对比 ai-agent-dev-system/skills/ 目录）
    ├── C.2 查阅术语定义（如「评审」「验收」「归档」的规范定义）
    ├── C.3 唤醒关联 Memory（如 pattern-review-fix-loop、anti-pattern-terminology-drift）
    └── C.4 查阅质量门禁检查清单（preference-quality-gate-checklist 对应阶段）
    ↓
开始执行技能
    ↓
执行阶段内容
    ↓
执行后必做收尾（迭代日志记录）
```

### 10.3 术语定义查阅速查表

| 术语 | 规范定义来源 | 常见理解偏差 | 正确理解 |
|-----|------------|-------------|---------|
| **归档** | OpenSpec.md 阶段3 | 标记完成 | 合并 specs/ + 移动 changes/ |
| **评审通过** | prd-review/architecture-review/code-review v1.1 | 有条件通过可进入下一阶段 | 只有「100% 通过」才是真正的通过 |
| **验收通过** | func-test v1.1 | 有条件通过可进入下一阶段 | 只有「100% 通过」才是真正的通过 |
| **提案** | OpenSpec.md 4.3 | 简单描述 | 声明变更目标、范围、非目标、依赖与风险 |
| **变更** | OpenSpec.md | 任意修改 | 待实施的提案，遵循 changes/ 目录结构 |

### 10.4 关联 Memory 唤醒清单

**执行各技能前建议唤醒的 Memory**：

| 技能 | 建议唤醒 Memory |
|-----|----------------|
| request-analysis | pattern-complete-quality-closed-loop（了解全流程） |
| prd-review | pattern-review-fix-loop, anti-pattern-conditional-pass-as-go |
| project-analysis | pattern-complete-quality-closed-loop |
| architecture-review | pattern-review-fix-loop, anti-pattern-conditional-pass-as-go |
| coding-implement | 项目特定的 project-rules/ |
| code-review | pattern-review-fix-loop, anti-pattern-conditional-pass-as-go, anti-pattern-terminology-drift |
| func-test | pattern-review-fix-loop, anti-pattern-conditional-pass-as-go, anti-pattern-terminology-drift |
| retrospective-analysis | pattern-five-stage-retrospective, pattern-breakthrough-thinking-redefine-problem-space |

### 10.5 执行前查阅声明模板

**执行任何技能前，填写以下声明**：

```markdown
**执行前查阅规范声明**

执行技能: [skill-name]  
执行阶段: [Step N: 阶段名称]  
执行日期: YYYY-MM-DD  

查阅确认:
- [ ] C.1 已确认 skill 版本为最新（[skill-path]/SKILL.md）
- [ ] C.2 已查阅本阶段关键术语定义（术语：[术语1], [术语2]）
- [ ] C.3 已唤醒关联 Memory（[memory1], [memory2]）
- [ ] C.4 已查阅质量门禁检查清单（preference-quality-gate-checklist Step N）

术语理解确认:
- [术语1]: 我的理解是 [描述]，与规范定义一致 ✓
- [术语2]: 我的理解是 [描述]，与规范定义一致 ✓

**签名**: [Agent 角色]  
**日期**: YYYY-MM-DD
```

### 10.6 违反处理

**未执行查阅规范即执行技能，视为违反本规则**：
- 执行产出可能不符合规范要求
- 需重新执行并补充查阅规范步骤
- 严重情况需启动复盘分析

---

**规则版本**: v1.2（新增执行前查阅规范机制）  
**最后更新**: 2026-03-17  
**关联文档**: OpenSpec.md, preference-quality-gate-checklist, anti-pattern-terminology-drift, anti-pattern-inertia-trap
