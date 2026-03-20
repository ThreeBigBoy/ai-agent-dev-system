# diagnose_startup：启动前环境诊断

## 是什么

`diagnose_startup.py` 是面向 **LangGraph 独立后端**（及本仓运行链路）的**本地诊断脚本**：一次性检查磁盘空间、Python 版本、内存、网络连通、配置与端口等（对应变更设计中的 P2-B 六项），输出表格或 JSON，便于在「起 uvicorn / 跑 MCP 之前」快速判断环境是否就绪。

## 有什么用

- 新机器或新 clone 后，确认本机是否满足运行后端的基本条件。
- 排查「后端起不来 / executor 报错」时，先缩小是环境问题还是业务逻辑问题。
- 作为 **`verify-minimal`** 流水线中的**第一步**（由该脚本子进程调用，见下节）。

## 当前使用方法

在 **ai-agent-dev-system 仓库根**执行（或通过 `--workspace` 指定根目录）：

```bash
python scripts/diagnose_startup/diagnose_startup.py
# 或显式指定工作区根
python scripts/diagnose_startup/diagnose_startup.py --workspace /path/to/ai-agent-dev-system
```

- 默认输出人类可读的检查结果表。
- 需要机器可读输出时加 `--json`。

## 被谁自动调用

| 调用方 | 说明 |
|--------|------|
| **`scripts/verify-minimal/verify_minimal.py`** | 会以子进程方式执行本脚本（`--workspace` 指向仓库根）。 |
| **`langgraph_backend` / `uvicorn` / MCP** | **不调用**。 |
| **`scripts/check-langgraph-backend/check_langgraph_backend.py`** | **不调用**（自检脚本自行请求 HTTP 与检查环境变量等）。 |

其余场景均为**人工在终端执行**或你在 **CI** 中显式编排。

## 相关文档

- 仓库根 [`新用户快速开始.md`](../../新用户快速开始.md) §5.2
- [`scripts/README.md`](../README.md)
