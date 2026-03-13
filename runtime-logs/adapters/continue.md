## Continue 宿主下的运行日志采集（示意草案）

当在 Continue 等第三方宿主中使用本仓库规则时，推荐：

- 通过 Continue 提供的 API 调用钩子（如有）获取模型名称、tokens 使用与耗时信息；
- 若无法直接获取 tokens，可使用 `metering_method: estimation` 并记录估算方法；
- 采用与 `runtime-logs/model-calls/*.jsonl` 一致的字段结构，将记录写入本地工作区中的 `runtime-logs/`。

具体实现可在后续变更中细化，并根据第三方宿主的能力与限制进行调整。

