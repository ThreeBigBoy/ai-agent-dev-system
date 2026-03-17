# 框架缺陷记录：LangGraph 业务项目 workspace 解析问题

**发现时间**: 2026-03-16 23:45
**发现人**: 主 Agent（执行强制改进措施时）
**严重级别**: 高（阻塞业务项目执行）
**所属变更**: update-product-template-default-health-compliance-section（Proj01ShopifyTheme）

---

## 问题描述

LangGraph 后端无法正确执行业务项目（非 ai-agent-dev-system 本仓）的 tasks.md，即使正确传递了 workspace_root 或 workspace_projects 参数。

### 现象

1. **workspace_root 传递失败**:
   ```bash
   curl -X POST /run -d '{"change_id": "update-product-template-default-health-compliance-section", "workspace_root": "/Users/billhu/Cursor Projects/Proj01ShopifyTheme"}'
   ```
   日志显示: `workspace_root: null`，错误: "tasks.md 不存在于本仓或传入的 workspace_root"

2. **workspace_projects 传递超时**:
   ```bash
   curl -X POST /run -d '{"change_id": "...", "workspace_projects": "Proj01ShopifyTheme|/Users/billhu/Cursor Projects/Proj01ShopifyTheme"}'
   ```
   请求超时（120s+），无响应，无日志记录

3. **本仓执行正常**:
   - `test-langgraph-backend`、`theme-test-health-check` 可正常执行
   - 这些 change_id 要么在 ai-agent-dev-system 本仓有 tasks.md，要么是测试用的空任务

## 根本原因分析（待确认）

可能原因 1: **参数解析问题**
- 后端可能没有正确解析请求体中的 workspace_root/workspace_projects
- FastAPI Pydantic 模型可能未正确处理这些可选字段

可能原因 2: **路径查找逻辑问题**
- `config.py` 或 `parser.py` 中的路径查找逻辑可能优先使用本仓路径
- 传入的 workspace_root 被覆盖或忽略

可能原因 3: **JSON 编码/空格问题**
- workspace_root 包含空格（"/Users/billhu/Cursor Projects/..."）
- 可能需要 URL 编码或不同的序列化方式

## 影响范围

| 场景 | 影响 |
|------|------|
| ai-agent-dev-system 本仓变更 | ✅ 正常执行 |
| 业务项目（Proj01ShopifyTheme）变更 | ❌ 无法执行 |
| migrate-langgraph-backend 归档后 | ❌ 无法验证业务项目 |

## 临时绕过方案（不推荐长期使用）

1. **手动执行 + 明确标记**:
   - 手动执行任务
   - 在迭代日志中明确标记为「非框架级执行」
   - 记录「框架缺陷阻塞，待修复」

2. **将业务项目 tasks.md 复制到本仓**（不推荐）:
   - 破坏单仓管理原则
   - 导致变更归属混乱

## 修复建议

### 优先级 1: 修复 workspace_root 解析

文件: `langgraph_backend/server.py` 或 `config.py`

检查点:
- [ ] 确认 `RunRequest.workspace_root` 是否正确接收参数
- [ ] 确认 `parser.py` 或 `workflow.py` 是否正确使用 workspace_root
- [ ] 添加调试日志，打印接收到的 workspace_root 值

### 优先级 2: 修复 workspace_projects 解析

文件: `langgraph_backend/server.py`

检查点:
- [ ] 确认 `RunRequest.workspace_projects` 是否正确解析 "key|path" 格式
- [ ] 确认 `config.py` 中的项目查找逻辑
- [ ] 处理超时问题（可能卡在路径解析阶段）

### 优先级 3: 增加测试用例

- [ ] 添加业务项目执行测试用例（非本仓）
- [ ] CI 中验证 workspace_root/workspace_projects 参数
- [ ] 添加 E2E 测试：创建临时业务项目 → 执行 /run → 验证检查点

## 验证方法（修复后）

```bash
# 验证 1: workspace_root 方式
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "change_id": "update-product-template-default-health-compliance-section",
    "task_range": "2.1",
    "workspace_root": "/Users/billhu/Cursor Projects/Proj01ShopifyTheme"
  }'

# 期望: 返回 200，feedback 包含执行结果
# 验证: runtime-logs/langgraph-runs/*.jsonl 中有该 change_id 记录
# 验证: workspace_root 不为 null
```

```bash
# 验证 2: workspace_projects 方式
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{
    "change_id": "update-product-template-default-health-compliance-section",
    "task_range": "2.1",
    "workspace_projects": "Proj01ShopifyTheme|/Users/billhu/Cursor Projects/Proj01ShopifyTheme"
  }'

# 期望: 不超时，返回 200
```

## 关联文档

- `pattern-langgraph-mcp-multi-workspace-config.md`: 设计时的多项目配置方案
- `langgraph_backend/server.py`: 需要修复的代码
- `langgraph_backend/config.py`: 路径解析逻辑
- `langgraph_backend/parser.py`: tasks.md 解析逻辑

## 状态

- [x] 问题发现
- [x] 现象记录
- [x] 影响评估
- [ ] 根因确认（代码级调试）
- [ ] 修复实施
- [ ] 验证通过

---

**备注**: 此缺陷阻塞了「强制 LangGraph 执行」改进措施的落地，需要优先修复。
