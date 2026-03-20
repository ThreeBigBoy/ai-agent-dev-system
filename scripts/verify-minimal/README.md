# verify-minimal：LangGraph 管线最小验证

## 是什么

`verify_minimal.py` 用于在**本机**对 **V2.11.x LangGraph 管线**做一次「从头到尾」的**最小验收**：串联环境诊断、在进程内 **invoke** `workflow`（覆盖无 HC0 / 有 HC0 等场景说明见脚本顶部注释）、并在未加 `--skip-http` 且后端已启动时可选请求 `GET /health` 与 `GET /confirm/pending`。

## 有什么用

- **不启动 HTTP 服务**也能验证大部分 workflow 逻辑（诊断 + 本地图执行）。
- 与「只 curl 后端」互补：能发现 **openspec / design 确认文件 / 本地 import** 类问题。
- 文档与 onboarding 中常作为「最小验证脚本」引用（见 `新用户快速开始.md`、`AGENTS.md`、根 `README.md`）。

## 当前使用方法

在 **ai-agent-dev-system 仓库根**执行：

```bash
python scripts/verify-minimal/verify_minimal.py [--workspace /path/to/repo] [--skip-http] [--base-url URL] [--change-id CHANGE_ID]
```

- `--skip-http`：跳过对运行中后端的 HTTP 探测（后端未起时常用）。
- `--workspace`：仓库根；默认当前工作目录（若当前在子目录，脚本会尝试向上解析含 `openspec` 的目录）。
- `--change-id`：用于 workflow 验证的 change-id，默认脚本内有约定值，可按需覆盖。

## 被谁自动调用

| 调用方 | 说明 |
|--------|------|
| **`langgraph_backend` / MCP** | **不调用**。 |
| **`check_langgraph_backend.py`** | **不调用**。 |
| **本仓库 CI（若有）** | 仅当你们在流水线里显式增加该命令时才会执行；仓库默认不隐含触发。 |

本脚本会**自动以子进程调用**：

- `scripts/diagnose_startup/diagnose_startup.py`（见同目录 `verify_minimal.py` 内 `run_diagnose()`）。

## 相关文档

- [`scripts/diagnose_startup/README.md`](../diagnose_startup/README.md)
- [`scripts/check-langgraph-backend/README.md`](../check-langgraph-backend/README.md)（更重的一体化自检）
- 仓库根 [`新用户快速开始.md`](../../新用户快速开始.md) §5.2
