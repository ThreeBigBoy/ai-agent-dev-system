# 基于 Cursor Usage Monitor 数据写入迭代日志「使用模型」— 落地方案

本目录提供**与 Cursor Usage Monitor 插件同源数据**的 Python 脚本，供 Agent 在追加迭代日志时获取「最近一次请求的模型」并写入日志。

## 一、流程概览

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 1. Cursor 桌面端：用户使用 Composer/Agent（含 Auto 模式）                    │
│ 2. Cursor 后端：记录用量事件（含 model、tokens、cost）                       │
│ 3. Cursor Usage Monitor 插件：用 session token 调用 Cursor API 拉取用量     │
└─────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 4. 本方案：Agent 在「追加迭代日志」前执行 get_last_model.py                  │
│    - 脚本从 Cursor 本地 state.vscdb 读取 token（与插件同源）                 │
│    - 或从环境变量 CURSOR_SESSION_TOKEN 读取                                │
│    - 调用 Cursor API: POST /dashboard/get-filtered-usage-events        │
│    - 解析 usageEventsDisplay，取最近一条的 model 字段                        │
│    - 将模型名输出到 stdout                                                  │
└─────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ 5. Agent 按全局规范：先执行脚本（或读取其输出），将 stdout 作为「使用模型」     │
│    写入 design/documents/迭代日志.md 的单条记录（记录中写明 change-id）       │
└─────────────────────────────────────────────────────────────────────────┘
```

## 二、数据源说明（与 Cursor Usage Monitor 一致）

| 项目 | 说明 |
|------|------|
| **Token** | Cursor 本地 SQLite：`User/globalStorage/state.vscdb` 表 `ItemTable`，key=`cursorAuth/accessToken`。路径：macOS `~/Library/Application Support/Cursor/User/globalStorage/state.vscdb`；Windows `%APPDATA%\Cursor\User\globalStorage\state.vscdb`；Linux `~/.config/Cursor\User\globalStorage\state.vscdb`。 |
| **API** | `https://cursor.com/api`；用量事件：`POST /dashboard/get-filtered-usage-events`，body：`{ teamId: 0, startDate, endDate, page: 1, pageSize: 100 }`。 |
| **认证** | Cookie：`WorkosCursorSessionToken=<userId>::<jwt>` 或 `userId%3A%3Ajwt`（URL 编码）。若 token 为纯 JWT，脚本会从 JWT 解析出 userId 并拼成 Cookie。 |
| **响应** | `usageEventsDisplay` 数组，每项含 `timestamp`、`model`、`tokenUsage` 等；按时间取**最近一条**的 `model` 即为本次/刚完成的请求所用模型（含 Auto 时实际路由到的模型）。 |

## 三、使用方式

### 3.1 前置条件

- 已安装 **Cursor 桌面端**并登录（保证本地有 `cursorAuth/accessToken`）。
- **不需要**安装 Cursor Usage Monitor 扩展；本脚本与扩展使用同一数据源（Cursor 本地 token + 用量 API），但**独立运行**，不依赖扩展。
- Python 3.8+，依赖：`requests`（见 `requirements.txt`）。

### 3.2 运行脚本

```bash
# 在项目根或任意目录
python get_last_model.py
# 或指定 ai-agent-dev-system 下路径
python ai-agent-dev-system/scripts/cursor-usage-to-iteration-log/get_last_model.py
```

- **成功**：stdout 输出一行，即最近一次用量事件的模型名（如 `claude-sonnet-4-20250514`、`gpt-4o` 等）；若为 Auto 且 API 返回实际模型则为该模型名。
- **无事件或解析失败**：输出 `Auto（具体模型未暴露）`，Agent 可照常写入日志。
- **未登录/无 token**：输出 `—`，Agent 按规范填「—」。

### 3.3 Agent 侧约定（全局规范）

在 `projects-rules-for-agent.md` 的迭代日志「使用模型」约定中：

- 在**追加迭代日志前**，若项目或工作区存在可执行的 `get_last_model.py`（如 `ai-agent-dev-system/scripts/cursor-usage-to-iteration-log/get_last_model.py` 或项目内复制），则**先执行**该脚本并读取 **stdout**（trim 后）。
- 若 stdout 非空且非占位符（非 `—`、非 `Auto（具体模型未暴露）` 时可视为具体模型），则**使用该输出**作为本条记录的「使用模型」。
- 若脚本执行失败、超时或 stdout 为空/占位符，则按现有优先级：约定文件 → 用户说明 → 指定模型 → Auto（具体模型未暴露）→ `—`。

## 四、可选：写入约定文件

若希望「脚本结果同时写入约定文件」供多轮使用，可在脚本末尾增加：将 stdout 内容写入 `.cursor/current-model-for-iteration-log.txt`（或项目约定路径），Agent 仍可优先读该文件（与现有规范一致）。

## 五、安全与隐私

- Token 仅从本地 Cursor 状态读取或从环境变量读取，**不落盘到仓库**；脚本不向第三方发送数据，仅请求 `cursor.com`。
- 建议将 `CURSOR_SESSION_TOKEN` 放在 env 或本地配置中，勿提交到 git。

## 六、文件说明

| 文件 | 说明 |
|------|------|
| `get_last_model.py` | 主脚本：取 token → 调 API → 解析最近一条 model → 打印到 stdout。 |
| `requirements.txt` | Python 依赖（requests）。 |
| `README.md` | 本说明。 |

