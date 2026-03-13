---
type: pattern
title: 场景与记忆/检查清单的触发式执行保障
change-id: sys-rules-memory-refactor-v2-4
tags: [rules, governance, memory, execution-guarantee, scenario-trigger]
applicable-projects: [ai-agent-dev-system]
host-scope: [cursor, vscode, generic]
related:
  - memory/patterns/pattern-rules-and-memory-evolution-governance.md
  - memory/patterns/pattern-iteration-log-enforcement-and-usage.md
  - memory/patterns/pattern-openspec-change-workflow.md
---

# 场景与记忆/检查清单的触发式执行保障

## 背景与目标

「检查并同步 README/快速开始/SOP」只是**一种**场景下的执行保障；治理体系中存在多种**治理关键场景**，若仅靠临时记忆或用户提醒，容易遗漏。本模式定义一套**通用机制**：为每类场景绑定「触发条件」与「必读 memory / 必做 checklist」，使正确行为由**结构化的场景→记忆/清单绑定**保障，而不是依赖外部提醒。

## 通用原则

1. **场景**：任一在治理上敏感、易漏或易错的行为（如改规则、记迭代日志、写 runtime-logs、新建变更、判定 simple/heavy、新增 memory、提交前 review 等）。  
2. **触发**：当主 Agent 或执行方**进入该场景**（由任务类型、正在编辑的文件、或阶段判断）时，在**执行关键动作前**应加载对应的 memory 或执行对应的 checklist。  
3. **绑定**：在规则或 Agent 文档中**显式写出**「当 X 时，必须先读 Y / 必须执行 Z」，使绑定可被检索、可维护；新增场景时，在本模式的「场景→绑定表」与对应触发点同步更新。

## 场景 → 必读 memory / 必做 checklist 绑定表

| 场景 | 触发条件（何时进入） | 必读 / 必做 | 触发写入位置（谁要求执行） |
|------|----------------------|-------------|----------------------------|
| **修改规则层文件** | 本次任务涉及修改 `global-rules/*.md`、`agents/*.md`、`skills-rules-for-agent.md` | 必须先读 `memory/patterns/pattern-rules-and-memory-evolution-governance.md` 并按其中 checklist 执行（含 change-id 挂载、design/records、迭代日志、README/新用户快速开始/宿主 SOP 审视） | `.cursor/rules/agent.mdc` |
| **任务启动（任一任务）** | 每次收到用户任务指令并完成 simple/heavy 判定后 | 主动记忆唤醒：按任务类型与上下文检索并按需加载相关 memory（见 `agents/主Agent.md` 第 7 条与关键 memory 列表），遵守一跳克制 | `agents/主Agent.md` 第 7 条 |
| **迭代日志记录/收尾** | 在 change-id 上下文中完成 Agent/技能调用，即将作出完成性/交付性回复前 | 收尾前须自检已追加迭代日志；**heavy 模式或易漏场景下**建议先读 `pattern-iteration-log-enforcement-and-usage.md` 与 `anti-pattern-missing-iteration-log-in-agent-calls.md` 再执行收尾 | `projects-rules-for-agent.md` 第三章、`agents/主Agent.md` 收尾 |
| **写入 runtime-logs 前** | 决定向 runtime-logs 追加 model-calls 或 system-events 前 | 应先读 `pattern-runtime-logs-usage-playbook-for-agents.md` 与 `anti-pattern-runtime-logs-business-data-pitfall.md`，确保不混入业务/敏感数据、粒度符合约定 | `agents/主Agent.md` 运行日志与长期记忆段 |
| **新建 OpenSpec 变更 / 新建 change-id** | 用户发起新需求、新建变更或迭代，第一步执行前 | 必须先读 `OpenSpec.md` 第六节与 4.3 节，以及 `memory/patterns/pattern-openspec-change-workflow.md`，再建 design/documents 与 openspec/changes | `projects-rules-for-agent.md` 2.1 |
| **simple/heavy 判定** | 每次收到任务指令，做复杂度判定时 | 按 `projects-rules-for-agent.md` 1.6 执行；需操作化细节时读 `pattern-task-complexity-judgement-and-mode-switch.md` | `projects-rules-for-agent.md` 1.6、`agents/主Agent.md` 第 4 条 |
| **模型/配额选择** | 需要选择模型层级或做额度决策时 | 按 `projects-rules-for-agent.md` 第六章；需策略细节时读 `pattern-model-tiering-and-quota-governance.md` | `projects-rules-for-agent.md` 第六章 |
| **新增 memory 条目** | 决定沉淀长期记忆并调用 create_memory_entry 或手写 memory 前 | 必须先读 `memory/schema.md`，遵守 `related`、正文「关联模式」与克制机制（3～5 条 related、一跳加载） | `agents/主Agent.md` 长期记忆沉淀段 |
| **提交/合并前 review（规则或治理相关变更）** | 对涉及 rules、agents、memory/schema、入口 mdc 的变更做 review 时 | 检查：rules 是否仅结论级 HOW、对应 SKILL/memory 是否已更新、README/新用户快速开始/宿主 SOP 是否需同步并已在 design/records 中记录；可复用 pattern-rules-and-memory-evolution-governance 中的审视项 | 本 pattern、pattern-rules-and-memory-evolution-governance |

## 使用说明

- **主 Agent**：在任务启动时通过「主动记忆唤醒」覆盖与当前任务匹配的场景；在进入上表某场景时，按「触发写入位置」找到对应规则或 主Agent 段落，执行其中要求的「必读/必做」。  
- **维护者**：新增治理关键场景时，应 (1) 在本表增加一行；(2) 在对应触发位置（agent.mdc、主Agent.md 或 projects-rules）写入「当 X 时须先读 Y / 须执行 Z」，保证自动化保障不依赖临时记忆。

## 关联模式

- 改规则层时的完整 checklist 与 README/SOP 审视见 `pattern-rules-and-memory-evolution-governance.md`。  
- 迭代日志的强制要求与自检见 `pattern-iteration-log-enforcement-and-usage.md` 与 `anti-pattern-missing-iteration-log-in-agent-calls.md`。  
- OpenSpec 变更流程见 `pattern-openspec-change-workflow.md`。
