## 通用宿主下的 runtime-logs 集成说明（Generic Host, V2.3）

> 适用对象：无法归类为 Cursor / VSCode / Continue 的其他宿主环境（如纯 CLI、第三方 Agent 宿主等）。

### 1. 统一目标

- 在不依赖特定宿主 API 的前提下，为任意宿主提供一条**最低要求**的运行日志写入路径；
- 所有宿主都尽量复用统一脚本接口：  
  `python3 scripts/runtime-logging/append_cursor_model_call.py ...`

### 2. 最小接入方式

只要宿主具备执行本地 shell 命令的能力，即可按以下方式写入运行日志：

```bash
python3 scripts/runtime-logging/append_cursor_model_call.py \
  --change-id <change-id> \
  --agent-role <agent-role> \
  --skill <skill-or-empty> \
  --model-name <model-name-or-empty> \
  --host generic \
  --host-group other \
  --model-family host_builtin_primary \
  --model-provider unknown
```

脚本会在当前仓库根目录下的 `runtime-logs/model-calls/` 中，为当日追加一条 JSON Lines 记录，字段结构见 `runtime-logs/README.md`。

### 3. 自动化建议

- 若宿主支持事件钩子（如「任务完成」「命令执行完毕」）：
  - 在这些事件上挂载上述命令或等价的 shell 调用；
  - 将当前 `change-id` 与 `agent-role` 作为参数传入；
  - 在能力允许的情况下补充：
    - `--model-name`（实际模型名或抽象名称）；
    - `--metering-method` 与可见的 tokens / duration 信息（如未来脚本支持外部传入 tokens 字段）。

- 若宿主只支持手动执行命令：
  - 则可在主 Agent 提示下，由用户按需执行该命令；
  - 仍可保证记录结构与多宿主一致，后续分析时只需按 `host`/`host_group` 区分来源即可。

### 4. 与治理层规则的关系

- 何时触发 runtime-logs 记录、需要记录哪些抽象字段，仍由 `OpenSpec + global-rules + agents/主Agent.md` 中的规则决定；
- 本文档只约定在「Generic Host」场景下，如何把治理层决策转化为统一脚本调用，从而写入 `runtime-logs/`。

