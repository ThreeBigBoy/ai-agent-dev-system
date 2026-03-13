## `memory` Frontmatter 规范

本文件定义长期记忆条目的 frontmatter 结构与字段含义，依据「运行日志与长期记忆综合设计方案（V2.3）」。

### 必选字段

| 字段 | 说明 | 示例 |
| :--- | :--- | :--- |
| `id` | 记忆唯一标识 | `mem-openspec-change-workflow-001` |
| `title` | 记忆标题 | `OpenSpec 变更标准流程（最小实践）` |
| `type` | 记忆类型：`pattern` / `anti-pattern` / `preference` / `playbook` / `reflection` | `pattern` |
| `tags` | 内容标签（至少 1 个） | `[openspec, change-flow]` |
| `applicable_projects` | 适用项目列表：`[all]` 或具体项目标识 | `[ai-agent-dev-system]` |
| `host_scope` | 适用宿主环境列表 | `[cursor, vscode, continue, openai-codex, generic]` |
| `source_change_ids` | 来源的变更 ID 列表 | `[sys-infra-memory-v1]` |

### 建议字段

| 字段 | 说明 | 示例 |
| :--- | :--- | :--- |
| `created_at` | 创建日期 | `2026-03-12` |
| `last_reviewed_at` | 最后审阅日期 | `2026-03-12` |
| `maturity` | 成熟度：`draft` / `experimental` / `stable` / `deprecated` | `draft` |
| `owner` | 维护责任人（可选） | `@billhu` |

### 示例：pattern 类型

```yaml
---
id: mem-openspec-change-workflow-001
title: OpenSpec 变更标准流程（最小实践）
type: pattern
tags: [openspec, change-flow, ai-agent-dev-system]
applicable_projects: [ai-agent-dev-system]
host_scope: [cursor, vscode]
source_change_ids: [sys-infra-memory-v1]
created_at: 2026-03-12
last_reviewed_at: 2026-03-12
maturity: draft
---
```

正文部分可采用 Markdown，自由描述模式的背景、步骤与适用场景；推荐结构：

1. 背景与适用场景
2. 推荐做法（步骤/Checklist）
3. 反例与常见误区（如有）
4. 与现有规范/技能的关系（如关联到某个 SKILL 或 OpenSpec 小节）

