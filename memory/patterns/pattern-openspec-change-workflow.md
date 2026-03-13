---
id: mem-openspec-change-workflow-001
title: OpenSpec 变更标准流程（最小实践）
type: pattern
tags: [openspec, change-flow, ai-agent-system]
applicable_projects: [ai-agent-dev-system]
host_scope: [cursor, vscode]
source_change_ids: [sys-infra-memory-v1]
created_at: 2026-03-12
last_reviewed_at: 2026-03-12
maturity: draft
---

# OpenSpec 变更标准流程（最小实践）

## 背景

在 `ai-agent-dev-system` 及其引用 OpenSpec 的项目中，任何研发级变更都应遵循统一的 change-id 流程，以保证文档、实现与验收的一致性。

## 推荐流程

1. **确定 change-id**
   - 按 OpenSpec 命名规范（动词开头、kebab-case）确定本次变更的唯一标识；
   - 若尚处于项目前期，则归属保留 change-id `project-early-phase`。
2. **先建 design/documents/[change-id]/**
   - 在 `design/documents/[change-id]/` 下至少创建一份需求或验收相关文档（如迭代需求说明、功能需求说明书、验收 Checklist 等）；
   - 如为架构或基础设施变更，可在此聚合背景与技术方案概览。
3. **再建 openspec/changes/[change-id]/**
   - 创建 `proposal.md`、`tasks.md`、可选 `design.md` 与 `specs/[capability]/spec.md`；
   - 在 `proposal.md` 中显式引用第 2 步中的 design/documents 文档，建立可追溯关系。
4. **按 tasks.md 推进实现与验证**
   - 将需求拆分为可勾选任务，标注负责人与（如适用）验收清单路径；
   - 编码、评审与验收均以 `tasks.md` 为单一任务真相来源。
5. **记录迭代日志与（可选）运行日志**
   - 在每次调用 Agent / 技能完成关键产出后，向 `design/documents/迭代日志.md` 追加一条记录；
   - 如有需要，可同时在 `runtime-logs/model-calls/*.jsonl` 中记录本次模型调用的技术指标。

## 适用场景

- 新增功能、架构调整、基础设施能力扩展（如本次 `sys-infra-memory-v1`）；
- 需要多 Agent / 多技能协作的复杂变更。

## 与规范和技能的关系

- 严格遵循 `OpenSpec.md` 第 5、6 节与 `global-rules/projects-rules-for-agent.md` 的变更启动顺序与迭代日志约定；
- 可与 `request-analysis`、`project-analysis`、`coding-implement`、`code-review`、`func-test` 等技能协同使用，形成从需求 → 方案 → 实现 → 评审 → 验收的闭环。

