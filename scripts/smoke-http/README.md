# smoke-http：LangGraph 后端 HTTP 冒烟

## 是什么

`smoke_http.sh` 是一个 **Bash** 小脚本：在 **LangGraph 后端已监听 HTTP**（默认 `http://127.0.0.1:8000`）时，用 `curl` 依次探测：

- `GET /health`
- `POST /run`（使用脚本内写死的示例 `change_id`）
- 若返回状态为 `waiting_hc0` / `waiting_hc2` / `waiting_hc7`，再请求 `GET /confirm/pending` 与 `GET /confirm/poll`（短时）

用于**联调/冒烟**，快速确认「服务进程活着且路由基本可用」。

## 有什么用

- 比手写多条 `curl` 更省事，适合复制到终端或嵌到本地脚本。
- **不替代** `verify-minimal`（后者侧重本地 workflow + 诊断）；也不替代 `check-langgraph-backend`（后者含 MCP 配置、留痕、多项目等）。

## 当前使用方法

在 **ai-agent-dev-system 仓库根**执行：

```bash
chmod +x scripts/smoke-http/smoke_http.sh   # 仅需一次
./scripts/smoke-http/smoke_http.sh
# 或指定后端地址
./scripts/smoke-http/smoke_http.sh http://127.0.0.1:8000
```

脚本内 `CHANGE_ID` 默认为 `deepen-langgraph-v2-11-1`；若你环境无该变更，可将脚本中的变量改为本机存在的 `change_id`，或改用 `check-langgraph-backend` / 手动 `curl`。

## 被谁自动调用

| 调用方 | 说明 |
|--------|------|
| **`langgraph_backend` / MCP** | **不调用**。 |
| **`verify_minimal.py` / `diagnose_startup.py` / `check_langgraph_backend.py`** | **不调用**。 |

仅 **人工**或你在 **CI** 中显式执行。

## 相关文档

- [`agent_team_project/langgraph_backend/README.md`](../../agent_team_project/langgraph_backend/README.md)（运行与联调）
- [`scripts/check-langgraph-backend/README.md`](../check-langgraph-backend/README.md)
- 仓库根 [`新用户快速开始.md`](../../新用户快速开始.md)
