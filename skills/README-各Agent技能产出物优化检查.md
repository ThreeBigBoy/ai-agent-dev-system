# 各 Agent 技能产出物优化检查

> 对照「产品经理 + request-analysis」「架构 + project-analysis」的优化方式（REFERENCE 最小结构 + 自检清单），检查其余 Agent 是否也需要类似优化。

---

## 已做优化的技能

| Agent | 技能 | 产出物 | REFERENCE（最小结构 + 自检） | 说明 |
|-------|------|--------|------------------------------|------|
| 产品经理 | request-analysis | PRD/迭代需求说明、design/documents、specs 初稿 | ✅ `迭代需求说明-PRD最小结构与自检.md` | 8 类最小结构、自检清单、场景描述、设计产出物 |
| 架构 | project-analysis | design.md、project-rules、技术架构图/执行逻辑图/数据流图 | ✅ `技术方案与架构产出物-最小结构与自检.md` | design.md 最小结构、project-rules 建议结构、图示存放与引用、8 项自检 |

---

## 已完成的优化（有主导技能且产出结构化文档）

| Agent | 技能 | 产出物 | 新增 REFERENCE | 说明 |
|-------|------|--------|----------------|------|
| **架构** | code-review | 评审报告 `[change-id]-code-review.md` | ✅ `评审报告-最小结构与自检.md` | 4 类最小结构、6 项自检清单；SKILL、架构 Agent、skills-rules 已引用 |
| **测试** | func-test | 验收记录 `[change-id]-func-test.md` | ✅ `验收记录-最小结构与自检.md` | 5 类最小结构、6 项自检清单（含两轮 validate）；SKILL、测试 Agent、skills-rules 已引用 |
| **前端/后端** | coding-implement | 代码、tasks、info-* | ✅ `实现完成自检.md` | 7 项实现完成自检；SKILL、前端/后端 Agent、skills-rules 已引用 |

---

## 无需单独 REFERENCE 的 Agent

| Agent | 说明 |
|-------|------|
| **主 Agent** | 不直接执行某一技能；产出为任务拆解、审核意见、决策纪要等，已由主Agent.md 与 projects-rules 约定。 |
| **文档 Agent** | 无主导技能；维护 README、AGENTS.md、project.md 等，结构要求已在 OpenSpec 与 skills-rules 中约定。 |
| **Bug 修复 Agent** | 无主导技能；配合 code-review、func-test，产出为代码修复与 tasks 更新，无需单独产出物 REFERENCE。 |

---

## 联动技能（image-analysis）

- **定位**：为 request-analysis、project-analysis、coding-implement（前端）提供图片解析结果，解析结论写入需求/spec、design.md/project-rules 或实现说明。
- **现有**：REFERENCE 有 spec-image-analysis-general、spec-image-analysis-openspec-integration。
- **结论**：产出为「解析结论」而非独立交付文档，由调用方（产品经理、架构、前端）按各自 REFERENCE 纳入；**不单独做「最小结构+自检」REFERENCE**。

---

## 实施建议

1. **code-review**：新增 `REFERENCE/评审报告-最小结构与自检.md`，并在 SKILL.md、子Agent-架构 中引用。
2. **func-test**：新增 `REFERENCE/验收记录-最小结构与自检.md`，并在 SKILL.md、子Agent-测试 中引用。
3. **coding-implement**：新增 `REFERENCE/实现完成自检.md`，并在 SKILL.md 中引用；前端/后端 Agent 描述中可增加「实现完成后须通过实现完成自检」。
4. **OpenSpec / skills-rules**：若 OpenSpec 或 skills-rules 中有对评审记录、验收记录路径的表述，可补充「结构与自检见对应技能 REFERENCE」。
