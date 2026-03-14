## `runtime-logs/`：运行日志体系

本目录用于存放 `ai-agent-dev-system` 在多宿主环境（Cursor、VSCode、第三方等）下的**运行日志**，聚焦技术指标与系统事件，而不记录具体业务内容或代码细节。

### 定位

- 记录模型调用的资源消耗（tokens、耗时）与状态（success / error / rate_limited 等）；
- 记录 Agent 执行过程中的关键系统事件（任务开始/结束、降级重试等）；
- 与 `design/documents/迭代日志.md` 互补：  
  - **运行日志**：技术指标、系统健康度；  
  - **迭代日志**：change-id 维度的业务过程与 Agent/技能调用记录。

> 隐私与安全约束：禁止在本目录中记录完整 Prompt/回复、业务数据正文、密钥、Token、Cookies 等敏感信息，仅允许脱敏后的摘要与统计指标。

### 目录结构

```text
runtime-logs/
├── .gitignore          # 忽略 .jsonl / .log 等运行期产物
├── README.md           # 本说明文档
├── model-calls/        # 模型调用明细日志（JSON Lines）
├── system-events/      # 系统事件文本日志
├── langgraph-runs/     # 新管线（LangGraph）执行留痕（JSONL，每行一次 /run 或 /resume）
└── adapters/           # 各宿主日志采集适配说明（非代码）
```

### `langgraph-runs/`：新管线执行留痕（系统日常运行合法目录）

- **用途**：LangGraph 后端每次 `/run`、`/resume` 成功后（或失败时）由后端自动追加一条记录，作为**新管线的唯一留痕**；不依赖 `design/documents/迭代日志.md` 或 `design/documents/` 下任何文件。
- **写入方**：`agent_team_project/langgraph_backend/server.py`；留痕根目录为 `ai-agent-dev-system/runtime-logs`（由 `AGENT_TEAM_PROJECT_ROOT` 指向本仓时解析）。
- **文件**：`langgraph-runs/YYYY-MM-DD.jsonl`，按日分片，每行一条 JSON。
- **字段**：`ts`、`change_id`、`thread_id`、`workspace_root`（解析出的项目根，可选）、`project_key`（命中的业务项目 key，可选）、`status`、`task_count`、`latency_seconds`、`checkpoint_id`（可选）、`error`（失败时）。
- **约定**：仅记录执行元数据与结果状态，不记录完整 feedback/results 正文，符合隐私与安全约束。

### `model-calls/*.jsonl` 数据格式（示例）

每条记录为一行 JSON，字段设计与方案文档保持一致（仅示例关键字段）：

```json
{
  "timestamp": "2026-03-10T10:15:30+08:00",
  "change_id": "sys-infra-memory-v1",
  "agent_role": "主Agent",
  "skill": null,
  "host": "cursor",
  "host_group": "whitelist",
  "session_id": "uuid-or-session-hash",
  "model_family": "host_builtin_primary",
  "model_provider": "cursor_builtin",
  "model_name": null,
  "metering_method": "none",
  "tokens": {
    "prompt": null,
    "completion": null,
    "total": null
  },
  "duration_ms": 4500,
  "status": "success",
  "error_info": null
}
```

不同宿主对 tokens / cost 的可见性不同，可通过 `metering_method` 字段标记计量方式（如 `none`、`openai_usage`、`cursor_usage_api`、`estimation` 等）。

### `system-events/events.log` 文本格式（示例）

```text
[2026-03-10 10:15:00] INFO  - 主Agent触发，change_id: 'sys-infra-memory-v1'，开始初始化 runtime-logs 目录。
[2026-03-10 10:20:30] INFO  - 已创建 memory 目录结构。
[2026-03-10 10:25:15] WARN  - 模型调用 (coding-implement) 失败，已按方案降级重试。
```

### 与宿主适配的关系

- 本目录仅定义**目标结构与数据规范**，具体采集与写入逻辑由 `platform-adapters/<host>/` 中的适配文档与工具脚本实现；
- 适配文档应说明：
  - 如何在对应宿主中获取模型调用的时间与资源消耗信息；
  - 如何将这些信息以 JSON Lines 或文本形式写入本目录；
  - 如何在不泄露业务敏感信息的前提下记录必要的诊断信息。

