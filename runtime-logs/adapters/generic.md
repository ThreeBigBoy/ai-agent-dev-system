## 通用宿主下的运行日志采集模板

对于未单独列出的宿主环境，可参考本模板实现最小可用的运行日志采集：

- 明确当前宿主能否获取以下信息：
  - 模型名称或抽象模型族（如「host_builtin_primary」）；
  - 请求耗时（毫秒）；
  - tokens 使用信息（如不可获取，可置为 `null` 并设置合适的 `metering_method`）。
- 选择合适的采集点（如调用 SDK 的封装层、客户端中间件或命令行工具），将采集到的信息以 `model-calls/*.jsonl` 格式写入本仓库的 `runtime-logs/` 目录。
- 系统事件可在任务生命周期关键节点（开始/结束/异常）写入 `system-events/events.log`。

所有实现需遵循：

- 不记录业务敏感数据，仅记录必要的技术指标；
- 默认本地落盘，不纳入 Git；
- 与 `ai-agent-dev-system/OpenSpec.md` 与 `global-rules/projects-rules-for-agent.md` 中的约定保持一致。

