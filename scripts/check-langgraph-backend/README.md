# scripts/check-langgraph-backend/：LangGraph 后端一键自检

一键验证 LangGraph 后端环境的完整性：从后端健康检查、环境变量、MCP 配置，到实际 `/run` 执行与留痕链路。

---

## 📋 何时使用本脚本

| 场景 | 推荐命令 |
|------|----------|
| **新环境装完依赖后** | `python scripts/check-langgraph-backend/check_langgraph_backend.py --skip-run` |
| **启动后端后验证** | `python scripts/check-langgraph-backend/check_langgraph_backend.py`（完整检查） |
| **怀疑配置/留痕异常时** | 完整检查 + 查看 `runtime-logs/` |

---

## 🚀 快速开始（复制即用）

```bash
# 1. 进入仓库根
cd /path/to/ai-agent-dev-system

# 2. 设置环境变量（必须）
# 自检第 2 项会校验该变量，未设置则该项不通过
export AGENT_TEAM_PROJECT_ROOT="/path/to/ai-agent-dev-system"

# 持久化（可选）：将上一行写入 ~/.zshrc 或 ~/.bash_profile，新开终端无需再输

# 3. 执行自检（完整 1～5 项）
python scripts/check-langgraph-backend/check_langgraph_backend.py

# 或：只做 1～3 项（不调用 /run）
# python scripts/check-langgraph-backend/check_langgraph_backend.py --skip-run
```

---

## 🔧 运行环境与目录

### 运行目录要求

> ⚠️ **重要**：以下命令均需在 **ai-agent-dev-system 仓库根目录**下执行。

**若当前不在仓库根**（例如在 `agent_team_project` 或其它子目录），先回到仓库根再执行自检：

```bash
# 方式一：若当前在 agent_team_project 下
cd ..

# 方式二：直接跳到本仓根（把路径改成你的实际路径）
cd /path/to/ai-agent-dev-system
# 如：cd /Users/billhu/Documents/AI\ OnePeace/AI\ Dev/01ProjectsDesignManage/ai-agent-dev-system

# 设置环境变量
export AGENT_TEAM_PROJECT_ROOT="$(pwd)"
# 然后执行下方表格中任一命令
```

**若不想切目录**，可将命令里的 `scripts/` 改为 `../scripts/`：
```bash
python ../scripts/check-langgraph-backend/check_langgraph_backend.py
```

---

## 💾 环境变量持久化

### 一键写入配置（推荐）

在 **ai-agent-dev-system 仓库根目录**下执行下面整段，即可写入当前路径，无需改路径、可直接拷贝用：

```bash
# 在仓库根执行（路径含空格也能正确写入）
REPO_ROOT=$(pwd)
echo "export AGENT_TEAM_PROJECT_ROOT=\"$REPO_ROOT\"" >> ~/.zshrc
source ~/.zshrc
```

> 💡 **使用 bash？** 将 `~/.zshrc` 改为 `~/.bash_profile` 或 `~/.bashrc`。

### 修复错误写入

若之前写入失败（路径含空格导致 source 报错），先删掉错误行再重写：

```bash
# 删除 ~/.zshrc 中与 AGENT_TEAM_PROJECT_ROOT 相关的错误行及可能被拆出的路径残行
grep -v 'AGENT_TEAM_PROJECT_ROOT' ~/.zshrc | grep -v 'OnePeace/AI' > ~/.zshrc.tmp && mv ~/.zshrc.tmp ~/.zshrc
# 再在仓库根执行上方的 REPO_ROOT=... 两行重新写入
source ~/.zshrc
```

> ⚠️ 若仍报错，可用 `cat -n ~/.zshrc` 查看行号，手动编辑删除报错所指的那几行。

### 验证是否生效

```bash
echo "$AGENT_TEAM_PROJECT_ROOT"
```

- ✅ 应输出为**完整**本仓根路径（以 `ai-agent-dev-system` 结尾）
- ❌ 若只输出到 `.../Documents/AI` 等中间段，说明写入时未加引号，需按上方「修复错误写入」清理后重写

新开终端再执行一次，输出完整路径则持久化成功。

### 生效周期

| 操作 | 变量是否生效？ |
|------|----------------|
| 重新打开终端 | ✅ 新终端会读 `~/.zshrc` |
| 重新打开工作区 / 重新启动 IDE | ✅ 之后新开的终端同样会读配置文件 |
| 仅需重新执行持久化命令的情况 | 本仓路径变更，或删改了配置文件 |

---

## 🎯 细分场景快速参考（一键复制）

> 💡 脚本按组合执行检查项，不支持单拆某项。

| 场景 | 命令（复制即用） |
|------|------------------|
| **只验证环境不跑任务**（装完依赖后） | `python scripts/check-langgraph-backend/check_langgraph_backend.py --skip-run` |
| **完整验证**（1～5 项，启动后端后） | `python scripts/check-langgraph-backend/check_langgraph_backend.py` |
| **仅验证本仓 change-id**（1/2/4，只跑本仓 /run） | `python scripts/check-langgraph-backend/check_langgraph_backend.py --local-only --local-change-id migrate-langgraph-backend` |
| **仅验证业务项目 change-id**（1/2/3/5，mcp.json 已配置） | `python scripts/check-langgraph-backend/check_langgraph_backend.py --business-only --business-change-id update-theme-v1.0.2` |
| **仅验证业务项目 change-id**（1/2/5，mcp.json 未配置，需传 workspace-projects） | `python scripts/check-langgraph-backend/check_langgraph_backend.py --business-only --workspace-projects "Proj01ShopifyTheme|/path/to/Proj01ShopifyTheme" --business-change-id update-theme-v1.0.2` |
| **完整验证 + 指定业务项目**<br>mcp.json **已配置**，只需指定 change-id | `python scripts/check-langgraph-backend/check_langgraph_backend.py --business-change-id update-theme-v1.0.2` |
| **完整验证 + 指定业务项目**<br>mcp.json **未配置**，需传 workspace-projects | `python scripts/check-langgraph-backend/check_langgraph_backend.py --workspace-projects "Proj01ShopifyTheme|/path/to/Proj01ShopifyTheme" --business-change-id update-theme-v1.0.2` |
| **只验证 MCP 配置的多项目目录** | `python scripts/check-langgraph-backend/check_langgraph_backend.py --skip-run`（第 3 项自动解析 mcp.json） |
| **指定后端地址**（非默认 8000 端口） | `python scripts/check-langgraph-backend/check_langgraph_backend.py --base-url http://127.0.0.1:8001` |

### 参数说明

- `--skip-run`：只执行 1～3 项（health、环境变量、MCP 目录校验），不调用 `/run`、不检查留痕
- `--local-only`：只验证本仓（执行 1/2/4），完全忽略 LANGGRAPH_WORKSPACE_PROJECTS 与业务项目 /run
- `--business-only`：只验证业务项目（执行 1/2/3/5），不执行本仓 /run（第 4 项）
- 默认（不加 `--skip-run` / `--local-only` / `--business-only`）：执行 1～5 项完整检查
- 第 5 项（业务项目 /run）：若 `~/.cursor/mcp.json` 未配置 `LANGGRAPH_WORKSPACE_PROJECTS` 且未传 `--workspace-projects`，会自动 SKIP
- **交互式输入**：在终端直接运行且未加 `--no-prompt` 时，会先询问「本仓 change-id」或「业务项目 change-id」（取决于是否开启 `--local-only` / `--business-only`）；回车用默认值，业务项输入 `skip` 可跳过第 5 项

---

## 📊 自检项说明

| 序号 | 检查项 | 判定标准 |
|:----:|--------|----------|
| 1 | GET /health | 返回 `{"status":"healthy"}` |
| 2 | AGENT_TEAM_PROJECT_ROOT | 指向含 `openspec/changes` 的本仓根 |
| 3 | LANGGRAPH_WORKSPACE_PROJECTS | 从 `~/.cursor/mcp.json` 解析并验证目录存在 |
| 4 | 本仓 /run + 留痕 | 执行 `POST /run` 并检查 `runtime-logs/langgraph-runs/` 有新增记录 |
| 5 | 业务项目 /run + 留痕 | 同上，未配置 `workspace_projects` 时 SKIP |

---

## 🔨 完整参数列表

| 参数 | 说明 | 示例 |
|------|------|------|
| `--skip-run` | 只执行 1～3 项，不调用 /run | `--skip-run` |
| `--local-only` | 只验证本仓（执行 1/2/4），忽略 LANGGRAPH_WORKSPACE_PROJECTS 与业务项目 /run | `--local-only` |
| `--business-only` | 只验证业务项目（执行 1/2/3/5），不执行本仓 /run | `--business-only` |
| `--no-prompt` | 不询问 change-id，使用默认或命令行参数（非交互/CI 时用） | `--no-prompt` |
| `--base-url` | 后端 URL | `--base-url http://127.0.0.1:8000` |
| `--local-change-id` | 本仓自检用的 change-id | `--local-change-id check-langgraph-backend` |
| `--business-change-id` | 业务项目自检用的 change-id | `--business-change-id 2026-03-14-update-theme-v1.0.2-mvp-health-compliance` |
| `--workspace-projects` | 业务项目列表 | `--workspace-projects "key1|path1:key2|path2"` |

---

## 📝 脚本执行留痕

每次执行（无论通过/失败/异常），自动写入系统事件：

| 项目 | 说明 |
|------|------|
| **位置** | `runtime-logs/system-events/events.log` |
| **格式** | `[时间] INFO - script_run check-langgraph-backend: exit_code=..., duration_ms=...` |

查看最近执行记录：

```bash
tail -n 5 runtime-logs/system-events/events.log
```

---

## 📚 相关文档

| 文档 | 内容 |
|------|------|
| **首次安装/启动** | [`新用户快速开始.md`](../../新用户快速开始.md) §5.1 / §5.2 |
| **快速参考卡片** | [`memory/playbooks/playbook-langgraph-backend-quickstart.md`](../../memory/playbooks/playbook-langgraph-backend-quickstart.md) |
| **规范与变更** | [`openspec/changes/check-langgraph-backend/`](../../openspec/changes/check-langgraph-backend/) |
