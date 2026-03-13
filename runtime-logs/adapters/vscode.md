## VSCode 宿主下的运行日志采集（示意草案）

本仓库在 VSCode 场景下的运行日志采集，可参考 Cursor 方案并结合实际插件/扩展能力实现：

- 若使用官方 GitHub Copilot / Copilot Chat，可参考其提供的使用统计接口（如有）；
- 若通过自定义扩展调用 OpenAI 兼容 API，可直接使用响应中的 `usage` 信息生成 `model-calls/*.jsonl` 记录；
- 系统事件可由扩展在关键命令执行前后写入 `system-events/events.log`。

所有采集逻辑应遵守方案文档与 `runtime-logs/README.md` 中的安全与隐私约束。

