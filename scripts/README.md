# scripts/：项目自动化脚本（OpenSpec 约定）

本目录为项目根下的**标准子目录**，统一存放自动化脚本（本地初始化、配置校验、工具型脚本等）。命名与用法须受 `openspec/project.md` 与 `design/project-rules/` 约束。

## 脚本一览

| 脚本 | 用途 | 用法示例 |
|------|------|----------|
| **check-langgraph-backend/** | LangGraph 后端一键自检（health、AGENT_TEAM_PROJECT_ROOT、LANGGRAPH_WORKSPACE_PROJECTS、本仓/业务 /run 与留痕） | `python scripts/check-langgraph-backend/check_langgraph_backend.py`，可选 `--skip-run`、`--base-url`；见 `check-langgraph-backend/README.md` |
| **diagnose_startup/** | 启动问题环境诊断（磁盘/Python/内存/网络/配置/端口等） | `python scripts/diagnose_startup/diagnose_startup.py --workspace /path/to/ai-agent-dev-system`；见 `diagnose_startup/README.md` |
| **verify-minimal/** | LangGraph 管线最小验证（diagnose + 本地 invoke；可选 HTTP） | `python scripts/verify-minimal/verify_minimal.py [--workspace /path/to/repo] [--skip-http]`；见 `verify-minimal/README.md` |
| **smoke-http/** | 后端已启动时的 HTTP 冒烟测试（/health、/run、/confirm/pending/poll） | `./scripts/smoke-http/smoke_http.sh [BASE_URL]`；见 `smoke-http/README.md` |
| **cursor-usage-to-iteration-log/** | 迭代日志相关 | 见 `cursor-usage-to-iteration-log/README.md` |
| **memory/** | 记忆条目创建 | 见 `memory/README.md` |
| **runtime-logging/** | 运行日志追加与汇总 | 见 `runtime-logging/README.md` |

## check-langgraph-backend 用法（从仓库根运行）

```bash
export AGENT_TEAM_PROJECT_ROOT="/path/to/ai-agent-dev-system"   # 必须
python scripts/check-langgraph-backend/check_langgraph_backend.py
```

- `--skip-run`：只执行 1～3 项（health、环境、MCP 配置目录），不执行 /run 与留痕检查  
- `--base-url`：后端 URL，默认 `http://127.0.0.1:8000`  
- `--local-change-id`、`--business-change-id`、`--workspace-projects`：覆盖默认自检用的 change-id 与项目列表  

详见 `scripts/check-langgraph-backend/README.md` 与 `openspec/changes/check-langgraph-backend/`。
