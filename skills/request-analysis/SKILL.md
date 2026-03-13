---
name: request-analysis
description: 分析用户需求并产出结构化文档；当用户输入「分析需求」等指令时，根据需求类型（新增/修改）在 design/documents/ 与 openspec/ 下创建本次需求对应的前期方案文档、工程规范与变更提案，包括：为本次需求创建 documents 子目录、初始化或更新 openspec/AGENTS.md 与 openspec/project.md，以及在 openspec/changes/[change-id]/ 下创建变更目录与 specs 结构化需求分析文档与任务拆分文档；若涉及前端或图片，可联动 image-analysis 技能解析图片内容。
---

# 需求分析技能

## 触发场景

- 用户输入「分析需求」「需求分析」「帮我分析这个需求」等。
- 用户提供一段功能描述或业务目标，希望转化为可执行方案与任务。
- 项目已按 `ai-agent-dev-system/OpenSpec.md` 初始化 `openspec/` 时，需产出符合 OpenSpec 的变更提案与文档。

## 整体流程

0. **（可选）加载与本次任务相关的长期记忆**  
   - 根据当前项目根目录、宿主类型与本次任务的关键词（如「openspec」「change-flow」等），在根级 `memory/` 目录下检索符合 `applicable_projects`、`host_scope` 与 `tags` 条件的 pattern / anti-pattern / preference / playbook / reflection 条目；  
   - 将筛选出的少量高相关记忆作为参考上下文，用于优化后续需求分析与任务拆分，但不替代本技能自身的规范流程。

1. **确定本次需求与 change-id**  
   - 从用户输入与上下文中识别本次需求的名称与范围。  
   - 若已给出或已存在对应变更目录，则沿用 `openspec/changes/[change-id]/`；否则按 OpenSpec 规范为本次需求确定一个新的 `change-id`（kebab-case，动词开头，如 `add-health-food-theme-mvp`）。

2. **产出项目前期方案（design/documents/[change-id]/）**  
   - 在 `design/documents/` 下为本次需求创建子目录：`design/documents/[change-id]/`。  
   - 在该子目录下创建或补充（命名可按项目实际约定微调）：  
     - `市场研究与产品方案.md`  
     - `功能需求说明书.md`  
     - `需求验收Checklist.md`（或 `需求验收清单.md`）  
     - （可选）`技术方案说明书.md` 等补充文档  
     - **迭代类/PRD 类**需求可采用单文档 `迭代需求说明.md` 覆盖下述 8 类内容，结构见 [迭代需求说明-PRD最小结构与自检](REFERENCE/迭代需求说明-PRD最小结构与自检.md)。  
   - 所有内容均围绕「本次 change-id 对应的需求」展开，便于与后续 `openspec/changes/[change-id]/` 建立一一对应关系。  
   - **自检**：产出后须按 [迭代需求说明-PRD最小结构与自检](REFERENCE/迭代需求说明-PRD最小结构与自检.md) 中自检清单过一遍，确保达到**可商业化、可技术落地、可验收、可衡量**；不满足时补全再进入步骤 3。

3. **初始化或更新 openspec/ 目录结构与项目宪法文件**  
   - 若项目根目录**不存在** `openspec/` 或其中**不存在** `openspec/AGENTS.md`：  
     - 按 `ai-agent-dev-system/OpenSpec.md` 规范初始化 `openspec/` 目录与 `openspec/AGENTS.md`，为项目建立基础协作规则。  
   - 若项目根目录**不存在** `openspec/project.md`：  
     - 结合当前项目实际情况，初始化 `openspec/project.md`，约定项目定位、开发环境、架构模式、技术栈、目录结构、命名与格式等顶层规则（作为项目宪法）。  
   - 若 `openspec/AGENTS.md` 或 `openspec/project.md` 已存在：  
     - 对比本次需求与现有约定，若发现有需要在协作规则或顶层约定层面补充说明的内容（如：新增协作习惯、引入新平台、约束发生变化等），则进行适度更新；若本次需求不触及这些顶层约定，则可记录为「本次需求无需修改 AGENTS.md / project.md」。

4. **识别需求类型：新增类 vs 修改类**  
   - 结合现有 `openspec/specs/` 与本次需求描述：  
     - **新增类**：新功能、新模块、新能力，当前 `openspec/specs/` 中无对应能力。→ 使用 [新增类需求分析 spec](REFERENCE/新增类需求分析spec.md)。  
     - **修改类**：在已有能力上扩展、调整或移除行为，或影响现有 specs。→ 使用 [修改类需求分析 spec](REFERENCE/修改类需求分析spec.md)。  
   - 在识别过程中，如对「是否为新增能力」存在不确定，应主动向用户提问确认。

5. **创建或更新 OpenSpec 变更目录与结构化 spec（openspec/changes/[change-id]/）**  
   - 在 `openspec/changes/` 下创建或补充本次需求的变更目录：`openspec/changes/[change-id]/`。  
   - 在该目录下：  
     - 创建/更新 `proposal.md`：描述本次需求的背景、目标、范围、影响与风险等。  
     - 创建/更新 `tasks.md`：按 [任务拆分 spec](REFERENCE/任务拆分spec.md) 输出可勾选任务列表。  
     - 视情况创建/更新 `design.md`：记录与本次需求直接相关的关键技术/交互设计。  
     - 在 `openspec/changes/[change-id]/specs/[capability]/spec.md` 下，按 OpenSpec 规范编写结构化需求分析文档（ADDED / MODIFIED / REMOVED Requirements + Scenario），并与 `design/documents/[change-id]/` 中的文档相互引用。

6. **前端需求与图片（可选联动 image-analysis）**  
   - 若本次需求涉及前端界面、原型图、设计稿或用户提供截图/图片：  
     - 主动加载或引用 **image-analysis** 技能（若可用），解析图片中的布局、文案、组件与交互要点。  
     - 将解析结果纳入：  
       - `design/documents/[change-id]/功能需求说明书.md` 中的说明；  
       - 以及对应 `specs/[capability]/spec.md` 中的 Scenario（包括 UI 状态、文案、边界场景等）。

## 与 OpenSpec 的对应关系

| 产出物 | 位置 | 依据 |
|--------|------|------|
| 市场研究与产品方案、功能需求说明书等 | `documents/` | 项目约定或本技能约定 |
| 变更提案说明 | `openspec/changes/[change-id]/proposal.md` | `ai-agent-dev-system/OpenSpec.md` 3.3 |
| 任务清单 | `openspec/changes/[change-id]/tasks.md` | `ai-agent-dev-system/OpenSpec.md` 3.4 + REFERENCE/任务拆分spec.md |
| 技术设计（可选） | `openspec/changes/[change-id]/design.md` | `ai-agent-dev-system/OpenSpec.md` 3.5 |
| 规范增量 | `openspec/changes/[change-id]/specs/[capability]/spec.md` | `ai-agent-dev-system/OpenSpec.md` 3.6 + 新增/修改类需求分析 spec |

## 参考规范

- 变更 ID、能力命名、规范增量格式等：以 `ai-agent-dev-system/OpenSpec.md` 为准。
- 新增类分析步骤与产出：见 [REFERENCE/新增类需求分析spec.md](REFERENCE/新增类需求分析spec.md)。
- 修改类分析步骤与产出：见 [REFERENCE/修改类需求分析spec.md](REFERENCE/修改类需求分析spec.md)。
- 任务拆分粒度与格式：见 [REFERENCE/任务拆分spec.md](REFERENCE/任务拆分spec.md)。
- **迭代/PRD 类产出的结构与自检**：design/documents 下的迭代需求说明或 PRD 须采用 [REFERENCE/迭代需求说明-PRD最小结构与自检.md](REFERENCE/迭代需求说明-PRD最小结构与自检.md) 中的最小结构，产出后执行其中自检清单，使产出达到可商业化、可技术落地、可验收、可衡量。

## 注意事项

- 有待决议项或歧义时，主动向用户发问，不自行假设。
- 若项目存在 `openspec/AGENTS.md` 或 `project-rules/`，引用其中与需求、技术栈相关的约定，保持产出与项目宪法一致。
