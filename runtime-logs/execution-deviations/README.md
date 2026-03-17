## `execution-deviations/`：执行偏差记录

本目录用于存放**执行过程中发现的问题、偏差、不符合预期的情况**的即时记录，属于运行时审计留痕。

### 与 system-events/ 的区别

| 维度 | `system-events/` | `execution-deviations/` |
|------|-----------------|------------------------|
| 关注点 | 记录"发生了什么" | 记录"发现哪里不对" |
| 内容 | 任务启动/完成/失败等事件 | 具体问题/偏差的发现与分析 |
| 触发时机 | 关键节点自动触发 | 发现问题时人工记录 |

### 与"复盘"的区别（⚠️ 重要）

| 术语 | 执行偏差记录 | 复盘 |
|------|-------------|------|
| **本质** | 即时事实记录 | 事后方法论总结 |
| **存放位置** | `runtime-logs/execution-deviations/` | `design/documents/retrospectives/[level]/` |
| **核心问题** | "发现了什么偏差？" | "为什么？如何改进？" |
| **文档结构** | 自由格式 | 必须含 5 大结构（目标→过程→根因→改进→沉淀） |
| **产出时机** | 执行中发现问题时 | 变更归档后 |

**禁止混淆**：
- ❌ 不要把本目录下的文档称为"复盘"
- ❌ 不要试图"先写执行偏差记录草稿，再迁移到 retrospectives/"
- ✅ 复盘是独立的、一次性产出到正确位置的系统性总结

### 文件命名规范

```
[偏差类型]-[change-id]-[日期].md
```

示例：
- `fake-completion-discovered-2026-03-16-update-product-template.md`
- `execution-deviation-2026-03-16-change-init-process-deviation.md`
- `schema-error-found-2026-03-17-add-feature-x.md`

### 内容结构建议

1. **偏差描述**：发现了什么问题/偏差？具体表现是什么？
2. **影响评估**：对当前执行的影响范围、严重程度
3. **即时补救措施**：已经或计划采取的即时行动
4. **是否需要转化为长期改进**：
   - 是否需要在复盘时深入分析？
   - 是否需要沉淀为 anti-pattern 或 pattern？
   - 关联到哪个 change-id 的复盘或 memory

### 与复盘的工作流程

```
执行中发现偏差
    ↓
立即在 execution-deviations/ 记录（本目录）
    ↓
继续执行或采取补救措施
    ↓
变更归档后
    ↓
在 design/documents/retrospectives/ 进行复盘
    ↓
复盘时可以引用 execution-deviations/ 中的发现作为素材
    ↓
复盘产出方法论沉淀（可选转化为 memory）
```

### 关联文档

- `runtime-logs/README.md` - 运行日志体系整体说明
- `anti-pattern-retrospective-vs-execution-deviation-terminology-confusion.md` - 术语混淆的反模式警示
- `preference-terminology-glossary.md` - "执行偏差记录"与"复盘"的精确定义
- `pattern-retrospective-one-time-production.md` - 复盘一次性产出模式