## Cursor 宿主下的运行日志采集（示意草案）

> 本文档描述在 Cursor 宿主下，将模型调用与系统事件采集到 `runtime-logs/` 目录的建议思路。具体实现细节可在后续变更中细化或通过插件/脚本实现。

### 目标

- 在不泄露业务敏感信息的前提下，尽可能记录：
  - change_id / agent_role / skill 等关联字段；
  - 模型调用耗时与可见的 token 使用信息；
  - 调用状态（成功 / 失败 / 限流）与错误类型。

### 可能的采集途径

- 利用已有的 `tools/cursor-usage-to-iteration-log` 脚本获取最近一次模型调用的使用信息；
- 在执行关键任务（如某个 change-id 的实现或评审）结束后，由主 Agent 调用脚本并将结果转换为 `runtime-logs/model-calls/*.jsonl` 中的一条记录；
- 对于系统事件，可在关键节点（如「开始执行 sys-infra-memory-v1 第一阶段」）由脚本或 Agent 写入 `system-events/events.log`。

### 注意事项

- 严禁在日志中写入完整 Prompt、模型回复正文、代码 diff 等业务内容；
- 建议先从**手动/半自动采集流程**起步，在使用体验稳定后再考虑自动化集成。

