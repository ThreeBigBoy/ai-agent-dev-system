## Cursor 宿主下的 runtime-logs 集成说明（V2.3）

> 目标：在 Cursor 中为 `ai-agent-dev-system` 打通「模型调用 → `runtime-logs/model-calls/*.jsonl`」与「运行事件 → `runtime-logs/system-events/events.log`」的最小实现路径，配合方案文档《runtime-logging-and-agent-memory-integrated.md》的第二阶段要求。

### 1. 整体思路

- **采集点**：不直接从 Cursor 内部 API 取原始调用日志，而是利用已有/可控的脚本与 MCP 工具，在关键任务结束后记录**汇总级**调用信息。
- **写入位置**：
  - 模型调用：`runtime-logs/model-calls/YYYY-MM-DD.jsonl`
  - 系统事件：`runtime-logs/system-events/events.log`
- **数据内容**：遵循 `runtime-logs/README.md` 中的字段设计，只记录：
  - `timestamp` / `change_id` / `agent_role` / `skill` 等关键标识；
  - `host` / `host_group` / `model_family` / `metering_method` 等环境与计量信息；
  - `tokens`（在能拿到 usage 时）与 `duration_ms`；
  - `status` 与脱敏后的 `error_info`。

> 注意：Cursor 内置模型通常无法给出精确 tokens，推荐将 `metering_method` 设为 `none`，并将 `tokens` 各项置为 `null`。

### 2. 与现有工具链的衔接

当前仓库已有用于「从 Cursor 使用信息写入迭代日志」的工具链：

- 路径示例：`scripts/cursor-usage-to-iteration-log/`
  - 其中包含 `get_last_model.py` 等脚本，可在本地读取最近一次模型调用使用信息，并返回模型名称或占位符。

在 V2.3 阶段，推荐的最小方案是：

1. **主 Agent 在完成一次重要任务后**（例如某个 `change-id` 的需求分析或实现阶段结束）：
   - 先按 `projects-rules-for-agent.md` 要求，将调用记录写入 `design/documents/迭代日志.md`。
2. **随后由用户触发一次本地命令**：
   - 可选：通过 `python3 scripts/cursor-usage-to-iteration-log/get_last_model.py` 获取最近一次模型名称；
   - 执行：  
     `python3 scripts/runtime-logging/append_cursor_model_call.py --change-id <id> --agent-role <role> --skill <skill> [--model-name <name>]`  
     由脚本在 `runtime-logs/model-calls/YYYY-MM-DD.jsonl` 中追加一条记录。

### 3. 推荐最小 JSON 记录示例

```json
{
  "timestamp": "2026-03-12T22:18:50+08:00",
  "change_id": "sys-infra-memory-v1",
  "agent_role": "主Agent",
  "skill": null,

  "host": "cursor",
  "host_group": "whitelist",
  "session_id": null,

  "model_family": "host_builtin_primary",
  "model_provider": "cursor_builtin",
  "model_name": null,
  "metering_method": "none",
  "tokens": {
    "prompt": null,
    "completion": null,
    "total": null
  },
  "duration_ms": null,

  "status": "success",
  "error_info": null
}
```

在后续迭代中，可以逐步补充 `session_id`、`duration_ms` 或更精确的 `tokens` 信息，但不强制一次到位。

### 4. 系统事件写入建议

- **触发时机示例**：
  - 某个 `change-id` 的第二阶段采集试点开始/结束；
  - 运行日志写入出现失败或降级；
  - memory 检索或沉淀出现重要事件（可在第三阶段扩展）。
- **格式建议**：沿用 `runtime-logs/README.md` 的文本格式，例如：

```text
[2026-03-12 22:18:50] INFO  - 在 Cursor 中完成 sys-infra-memory-v1 第二阶段最小采集试点，已追加一条 model-calls 记录。
```

### 5. 与 runtime-integration 的关系

- `platform-adapters/cursor/runtime-integration.md` 负责说明「主 Agent 决策 → 运行后端」的执行链路。
- 本文件只聚焦：
  - 在该执行链路前后合适的时间点，将「一次任务的资源消耗与状态」追加到 `runtime-logs/`；
  - 保证不与 `design/documents/迭代日志.md` 的业务过程记录重复。

