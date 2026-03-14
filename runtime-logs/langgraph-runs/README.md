# langgraph-runs：新管线执行留痕

本目录由 LangGraph 后端在每次 `/run`、`/resume` 调用后自动写入，作为**新管线的唯一合法留痕**，不依赖迭代日志或 design/documents。

- **文件**：`YYYY-MM-DD.jsonl`，按日分片，每行一条 JSON。
- **字段**：`ts`（ISO8601）、`change_id`、`thread_id`、`workspace_root`（可选，解析出的项目根）、`project_key`（可选，命中的业务项目 key）、`status`、`task_count`、`latency_seconds`、`checkpoint_id`（可选）、`error`（失败时）。
- **写入**：`agent_team_project/langgraph_backend/server.py` 在请求结束时追加；留痕根为 `ai-agent-dev-system/runtime-logs`。
