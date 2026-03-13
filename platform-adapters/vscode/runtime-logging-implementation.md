## VS Code 宿主下的 runtime-logs 集成说明（V2.3）

> 目标：在 VS Code 官方 Agent Chat / 相关插件场景下，为 `ai-agent-dev-system` 提供一条与 Cursor 类似的、尽量简单的运行日志写入路径，满足方案文档第二阶段的「宿主适配与采集试点」要求。

### 1. 宿主特点与约束

- VS Code 官方 Agent Chat / Copilot Chat 等宿主通常不直接暴露底层模型调用 usage API；
- 对于通过自定义扩展或 CLI 调用 OpenAI 兼容 API 的场景，则可以获取精确的 `usage` 信息。

因此，本 adapter 区分两类场景：

1. **只使用官方 Agent（无法直接拿 usage）**：
   - 可仅记录抽象级别信息（`host: vscode` / `host_group: whitelist` / `model_family: host_builtin_primary` 等），`tokens` 与 `duration_ms` 可设为 `null`。
2. **通过扩展调用 OpenAI 兼容 API**：
   - 推荐在扩展的 HTTP 客户端中拦截响应的 `usage` 字段，并据此写入 `runtime-logs/model-calls/*.jsonl`。

### 2. 写入 `runtime-logs/model-calls/*.jsonl` 的最小实现思路

无论是否能精确拿到 usage，建议统一走一个本地脚本入口，例如（示意）：

```text
scripts/
└── runtime-logging/
    └── append_vscode_model_call.(ts|js|py)
```

扩展或本地命令在合适时机调用该脚本，并传入：

- `change_id`（如 `sys-infra-memory-v1`）；
- `agent_role`（如 `主Agent` / `前端 Agent` 等）；
- 可用范围内的模型信息（如 `model_name`、`metering_method`、`tokens` 等）。

脚本负责：

1. 计算 `timestamp`；
2. 确认/创建当日的 `runtime-logs/model-calls/YYYY-MM-DD.jsonl` 文件；
3. 以 JSON Lines 形式追加一条记录。

> 具体脚本实现可在后续变更中补充，本文件只约定输出位置与字段格式。

### 3. 系统事件日志的简单用法

对于 VS Code 场景，也推荐直接复用 `runtime-logs/system-events/events.log`，记录：

- 某个 change-id 的采集试点启停；
- runtime-logs 写入失败与降级信息；
- 与 memory 检索/沉淀相关的重要事件（可在第三阶段扩展）。

格式与 Cursor 一致，例如：

```text
[2026-03-12 22:18:50] INFO  - 在 VS Code 中执行 sys-infra-memory-v1 相关任务，准备写入一条 model-calls 记录。
```

### 4. 与 VS Code adapter 其他文档的关系

- `vscode/README.md` 与 `agents-entry.md`、`feedback-bridge.md` 等文档，负责解释：
  - 如何在 VS Code 中加载治理内核规则；
  - 如何把运行后端的结果带回 Agent 对话。
- 本文件补充说明：
  - 在上述运行链路前后，如何将对模型调用与系统事件的关键信息追加到 `runtime-logs/`；
  - 确保运行日志与 `design/documents/迭代日志.md` 的业务记录互补而不重复。

