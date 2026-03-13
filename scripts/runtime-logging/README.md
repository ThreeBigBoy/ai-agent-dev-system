## `scripts/runtime-logging/`：运行日志辅助脚本

本目录存放与 `runtime-logs/` 协作的简单脚本，当前包含：

- `append_cursor_model_call.py`：通用的模型调用记录追加脚本，可在 Cursor、VSCode 或其他宿主环境下，将一条模型调用记录追加到当日的 `runtime-logs/model-calls/YYYY-MM-DD.jsonl` 文件。
- `summarize_model_calls.py`：按日期 / change-id / host 等维度，对 `runtime-logs/model-calls/*.jsonl` 中的记录做简单汇总，输出到终端，便于主 Agent 或用户快速查看调用分布。

### 使用示例（从仓库根目录运行）

```bash
python3 scripts/runtime-logging/append_cursor_model_call.py \
  --change-id sys-infra-memory-v1 \
  --agent-role 主Agent \
  --skill request-analysis \
  --model-name auto
```

脚本会：

- 以当前本地时间生成 `timestamp` 字段；
- 在 `runtime-logs/model-calls/` 目录下创建（或复用）当日的 `YYYY-MM-DD.jsonl` 文件；
- 追加一条符合 `runtime-logs/README.md` 约定字段的 JSON 记录。

关键参数说明（带默认值的可按宿主覆盖）：

- `--host`：宿主标识（默认 `cursor`），如 `vscode`、`continue`、`generic` 等；
- `--host-group`：宿主分组（默认 `whitelist`），如 `third_party`、`other`；
- `--model-family`：抽象模型族（默认 `host_builtin_primary`）；
- `--model-provider`：模型提供方（默认 `cursor_builtin`）；
- `--metering-method`：计量方式（默认 `none`），可选 `openai_usage`、`cursor_usage_api`、`estimation` 等。

> 注意：当前版本不主动获取 tokens 与精确耗时，`tokens` 字段默认为 `null`，`duration_ms` 默认留空；可在后续迭代中根据宿主能力补充。

### 汇总脚本示例

```bash
# 按日期查看总调用次数与 status 分布
python3 scripts/runtime-logging/summarize_model_calls.py --group-by day

# 按 change-id 汇总
python3 scripts/runtime-logging/summarize_model_calls.py --group-by change-id

# 按 host 汇总
python3 scripts/runtime-logging/summarize_model_calls.py --group-by host
```

脚本会：

- 读取 `runtime-logs/model-calls/*.jsonl` 中所有记录；
- 按指定分组维度（day/change-id/host/day-change-id/all）统计总调用次数与不同 `status`（success/error/rate_limited 等）的数量；
- 以制表符分隔的形式输出到终端，便于主 Agent 或用户在需要时查看整体调用分布。

