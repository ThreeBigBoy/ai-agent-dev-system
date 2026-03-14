---
id: mem-playbook-langgraph-backend-quickstart-001
title: LangGraph 后端新环境安装与启动（新用户/新机器）
type: playbook
tags: [langgraph, backend, quickstart, env-setup, agent_team_project]
applicable_projects: [ai-agent-dev-system]
host_scope: [cursor, vscode, continue, openai-codex, generic]
source_change_ids: [migrate-langgraph-backend]
created_at: 2026-03-14
last_reviewed_at: 2026-03-14
maturity: stable
related:
  - memory/patterns/pattern-scenario-memory-trigger-governance.md
---

# LangGraph 后端新环境安装与启动

## 适用场景

- 第一次在新环境或新机器上使用 ai-agent-dev-system，需要跑 LangGraph 独立后端（多 Agent 协同执行）。
- 遇到「未安装 langchain-openai」或 executor 任务报错时，按本 playbook 从环境上解决。

## 推荐步骤

### 1. 安装依赖（新环境/新机器）

在 **`agent_team_project`** 目录下任选其一：

- **一键脚本**：`bash setup-langgraph-env.sh`（会创建 `.venv`、安装全部必装包并自检，含 `langchain-openai`）。
- **手动**：先 `source .venv/bin/activate`（或创建 `.venv` 后再激活），再执行 `pip install -r requirements.txt`。

完成后即可从环境上解决「未安装 langchain-openai」问题；若仅做流程/解析/状态接口验证，可不装，但 executor 任务会返回错误结果。

### 2. 配置 API 与启动后端（本机已装好依赖时）

- **配置**：在 `agent_team_project/.env` 或当前 shell 环境变量中配置 `OPENAI_API_KEY`（必填），以及可选的 `OPENAI_API_BASE_URL`。可复制 `.env.example` 为 `.env` 后填写，勿将 `.env` 提交版本库。
- **启动**：用该 .venv 启动后端即可正常跑 executor 任务：
  ```bash
  cd agent_team_project
  source .venv/bin/activate
  export AGENT_TEAM_PROJECT_ROOT="/你的/ai-agent-dev-system 仓库根路径"
  uvicorn langgraph_backend.server:app --host 127.0.0.1 --port 8000
  ```
- **验证**：`curl -s http://127.0.0.1:8000/health` 返回 `{"status":"healthy",...}` 即就绪。

## 与文档的对应关系

- 详细依赖清单、手动安装命令与「启动后端与 API 配置」见 **`新用户快速开始.md`** 第 5.1、5.2 节。
- MCP 配置与 Cursor 联调见 `platform-adapters/cursor/mcp-setup.md` 第 6 节与 `agent_team_project/MIGRATION.md`。
