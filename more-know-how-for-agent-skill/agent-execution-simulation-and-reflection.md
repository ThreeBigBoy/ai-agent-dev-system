# Agent 执行 projects-rules-for-agent.md 效果模拟与反思

> 从 AI 视角模拟单次对话内 Agent 按该规则文档执行的效果，并反思可改进点。  
> 与 `规范体系总览.md`、`projects-rules-for-agent.md` 配套使用。

---

## 一、模拟场景与执行轨迹

### 场景 A：用户说「帮我做首页加一个促销倒计时区块」

**假定**：当前在 Proj01ShopifyTheme 项目，已有 change-id = update-theme-v1.0.1-mvp-editor-ux，且 openspec/、design/documents/ 已存在。

| 步骤 | 规则依据 | 模拟行为 | 效果评估 |
|------|----------|----------|----------|
| 1 | 总则 + 一 1.1 | 识别为「新需求/新建变更或迭代」→ 主 Agent 统筹，须先走 2.1 OpenSpec 变更入口 | 需先读 OpenSpec §6、§4.3；若未读会违规 |
| 2 | 二 2.1 | 读取 OpenSpec.md 第六节、4.3 节；确认是否已有 design/documents/[change-id]/ 或需新建 | 若 workspace 未挂 ai-agent-dev-system，无法读 OpenSpec → **路径依赖** |
| 3 | 一 1.2 | 判定任务类型：含「需求分析、方案设计、变更提案」→ 产品经理 Agent + request-analysis | 表中有明确映射，可执行 |
| 4 | 一 1.3 自检 | 执行方=产品经理 Agent；技能=request-analysis；须先读 skills/request-analysis/SKILL.md | 自检 1 要求「已读取 SKILL」→ **必须先有一次 read_file(SKILL.md)** |
| 5 | 一 1.3 自检 | 新建变更顺序：若本次为新 change-id，须先 design/documents 再 openspec/changes | 若用户未给 change-id，需生成或询问 → **规则未写「谁定 change-id、何时问用户」** |
| 6 | 执行 | 读 SKILL.md → 按步骤产出 design/documents/…、proposal、tasks 等 | 依赖 SKILL 内容质量 |
| 7 | 一 1.4 + 三 | 产出完成后：向 design/documents/[change-id]/records/迭代日志.md 追加一条 | 若 change-id 不明则「可跳过」→ 易被解释为不写日志 |
| 8 | 收尾自检 | 在说「已落实」「请验收」前自检：是否已追加日志 | 明确禁止先交付再补录，**有效约束** |

**模拟结论（场景 A）**：  
- **能执行到的**：任务类型→执行方→技能、先读 SKILL、迭代日志收尾。  
- **已优化**：① 路径不可达时按 2.1 第 4 款降级（.cursorrules、AGENTS.md、先 design 再 openspec）；② change-id 由主/产品经理在产出 proposal 时确定，符合 project.md 命名，用户指定则从用户；③ 自检 4 已收紧为「是否将在产出完成后、完成性回复前追加一条」。

---

### 场景 B：用户说「推进 2.2」

**假定**：同一变更，tasks.md 中 2.2 已存在，负责人可能标注也可能未标注。

| 步骤 | 规则依据 | 模拟行为 | 效果评估 |
|------|----------|----------|----------|
| 1 | 二 2.2 | 主 Agent 读取 proposal、tasks、design/documents/… 下至少一份需求/验收文档 | 需明确「当前变更」的 change-id；若用户未说，需从上下文或 tasks 推断 |
| 2 | 二 2.2 | 根据 tasks 中 2.2 的负责人确定执行方；未标注则按任务性质指派 | 规则清晰；若 2.2 是「验收」类，须走 1.3 自检 3（验收清单与负责人） |
| 3 | 一 1.3 | 自检 1：执行方是否已读对应 SKILL？自检 4：是否约定迭代日志？ | 同上：执行方=己身时「约定」易被省略为「我会写」 |
| 4 | 执行 | 读 SKILL → 实施 → 产出 | 依赖 SKILL 与 tasks 描述一致 |
| 5 | 一 1.4 | 向 records/迭代日志.md 追加一条；收尾自检后再做完成性回复 | 强约束，能减少「忘写日志」 |

**模拟结论（场景 B）**：  
- **能执行到的**：读 proposal/tasks、按负责人或任务类型指派、先读 SKILL、迭代日志必追加。  
- **仍依赖**：①「当前变更」change-id 若未显式出现，需从打开的文件/路径推断；② 验证类任务「仅验收通过后方可勾选」——谁在哪个文件勾选、何时勾依赖 tasks.md 或项目约定。

---

### 场景 C：用户说「这段代码帮我改成用 TypeScript」

**假定**：无 change-id、无「新需求/迭代」表述，属单次小改动。

| 步骤 | 规则依据 | 模拟行为 | 效果评估 |
|------|----------|----------|----------|
| 1 | 一 1.1 | 判定任务类型：代码实现/重构 → 前端或后端 Agent + coding-implement | 表中有映射 |
| 2 | 一 1.3 | 自检 2：非新建变更，跳过。自检 4：无 change-id 上下文 → 「可跳过」迭代日志 | 规则允许不写日志，**与「所有调用均须记录」的严格解释有张力** |
| 3 | 一 1.4 | 无明确 change-id 时可跳过收尾 | 单次小改不会写日志，符合当前条文但若希望「凡有项目就记」需显式加例外 |
| 4 | 四～九 | 遵守代码规范、安全、行为规则（如 python3、不 rm -rf） | 分领域规则可被引用，无强制「先读 SKILL」外的二次自检清单 |

**模拟结论（场景 C）**：  
- 在项目内但用户未指明变更单时：归属 **`project-early-phase`**（见第三节 3.1），须向 `design/documents/project-early-phase/records/迭代日志.md` 追加一条；流程仍为定执行方→读 SKILL→执行→收尾必追加日志。

---

### 场景 D：立项研究、需求分析阶段（使用保留的 project-early-phase）

**假定**：新项目或已有 openspec/；用户说「先做立项研究」或「先出需求分析再定是否立项」——**尚未进入研发迭代**。

| 步骤 | 规则依据 | 模拟行为 | 效果评估 |
|------|----------|----------|----------|
| 1 | OpenSpec 5.1、6 总则 + 三 3.1 | **所有任务自项目一开始均须有 change-id**。项目前期使用各项目通用的保留 change-id **`project-early-phase`**（非研发迭代变更性质，供主 Agent、产品经理 Agent 开展早期工作） | 立项研究、需求分析等必须归属 project-early-phase |
| 2 | OpenSpec 6.3 + 三 3.1 | **必须**在首次进行项目前期工作时创建 **`design/documents/project-early-phase/`** 及 **`design/documents/project-early-phase/records/迭代日志.md`**；产出存放于 `design/documents/project-early-phase/`；每次在该上下文中调用 Agent/技能时**须**向该迭代日志追加一条 | 不得跳过日志；与研发变更同等强制 |
| 3 | 一 1.4 | 收尾与 1.4 必做，不得以「尚无研发变更」为由跳过 | 与有 change-id 时一致 |
| 4 | OpenSpec 5.1、6.3 | 一旦项目决定启动**首个研发变更**，新建自定 change-id（如 `init-mvp`），按 6.1 先 design/documents/[change-id]/ 再 openspec/changes/[change-id]/；此后的研发任务归属该 change-id，不再用 project-early-phase 作为研发任务的 change-id | 前期与研发阶段通过 change-id 明确切分 |

**模拟结论（场景 D）**：  
- 立项研究、需求分析等**必须**使用保留的 **`project-early-phase`**，须建目录与迭代日志，**不得**跳过。  
- 仅当**不在任何项目上下文中**（如纯泛化咨询、未打开项目）时可跳过迭代日志与 1.4 收尾。

---

## 二、整体执行效果反思

### 做得好的地方

1. **流程可追溯**：任务类型→执行方→技能→先读 SKILL，顺序固定，减少「直接开干」。
2. **收尾自检**：完成性回复前必须已追加迭代日志，且禁止先声称完成再补录，**对 AI 的约束可操作**。
3. **总则前置**：总则 5 条先于流程与分领域规则，价值取向（OpenSpec、配额、安全、简洁）在决策时易被带入。
4. **分领域清晰**：安全 MUST、配额 SHOULD、代码/行为/注释/补充分章，与规范体系总览一致，便于「查某类事看某章」。

### 已落实的优化（2026-02 修订）

1. **路径不可达时的降级**：2.1 第 4 款已明确：当无法访问 `ai-agent-dev-system/OpenSpec.md` 或 `ai-agent-dev-system/skills/` 时，以当前项目 `.cursorrules`、`openspec/AGENTS.md` 及项目内可见的 proposal/tasks 为准；并补充 **change-id 确定时机**（主/产品经理在产出 proposal 时确定，符合 project.md 命名，用户指定则从用户）。
2. **自检 4 收紧**：已改为「是否将在**本次调用产出完成后、作出完成性回复之前**，向对应 change-id 的迭代日志文档**追加一条**」，并区分项目前期（project-early-phase）与研发变更路径。
3. **所有任务必有 change-id（含项目前期）**：OpenSpec 5.1 与 6.3、projects-rules 第三节 3.1 已统一——**所有项目从一开始的所有任务都必须有 change-id**；项目前期（立项研究、需求分析等）使用各项目通用的保留 change-id **`project-early-phase`**，须建 `design/documents/project-early-phase/` 及 `records/迭代日志.md`，每次调用须追加一条；仅当**不在任何项目上下文中**时可跳过迭代日志与 1.4 收尾。

### 仍依赖项目或 tasks 的细节

4. **验证类任务勾选主体**：1.3 自检 3、2.2 第 4 步要求验收通过后再勾选；「谁在哪个文件勾选、勾选即视为通过」未在本文定义，依赖 tasks.md 或项目约定。

---

## 三、小结

从 AI 视角模拟后，**该规则文档**：（1）**所有项目从一开始的所有任务均须有 change-id**，项目前期使用保留的 **`project-early-phase`**，须建目录与迭代日志并每次追加；（2）研发迭代变更使用自定 change-id，按 OpenSpec 6.1 与本节执行；（3）**路径不可达**时按 2.1 第 4 款降级；（4）**仅当不在任何项目上下文中**时可跳过迭代日志与 1.4 收尾。仍依赖项目或 tasks 的仅有**验证类任务勾选主体与路径**，可留由 tasks.md 或 project.md 约定。
