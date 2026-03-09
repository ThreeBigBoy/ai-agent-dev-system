# VS Code 从 0 开始初始化配置 SOP 与 GUI 走查清单

## 1. 适用对象

适用于首次从 Git 下载 `ai-agent-dev-system`，希望在 **VS Code 官方 Agent Chat / GitHub Copilot** 下使用多 Agent 协同系统的用户。

## 2. 目标结果

完成本手册后，应达到以下状态：

1. VS Code 能读取根 `AGENTS.md`
2. 自定义 agent / mode 可读取 `.github/agents/*.agent.md`
3. 主 Agent 与子 Agent 在白名单宿主策略下优先使用宿主内置模型
4. 如需触发 runtime backend，可显式传入 `AGENT_HOST_TYPE=vscode`

## 3. 前置条件

- 已安装 Visual Studio Code
- 已安装 GitHub Copilot Chat
- 已将本仓库克隆到本机
- 已安装 Python 3

## 4. 初始化配置 SOP

### 4.1 打开仓库根目录

用 VS Code 打开：

- `ai-agent-dev-system/`

这样根 `AGENTS.md` 和 `.github/agents/*.agent.md` 都能被当前工作区看到。

### 4.2 安装 runtime 依赖

如需使用 `agent_team_project`，在仓库根目录执行：

```bash
pip3 install mcp jsonschema python-dotenv langchain-openai langgraph pydantic
```

### 4.3 准备个人 API 环境变量

即使 VS Code 属于白名单宿主，也建议准备 fallback API：

```env
OPENAI_API_KEY=your_key
OPENAI_API_BASE_URL=https://api.siliconflow.cn/v1
```

### 4.4 确认入口文件

应至少存在：

- 根 `AGENTS.md`
- `.github/agents/main.agent.md`
- `.github/agents/frontend.agent.md`
- `.github/agents/backend.agent.md`
- `.github/agents/test.agent.md`

### 4.5 如需接 runtime backend

若你希望在 VS Code 下也触发 `agent_team_project`，建议运行时显式传入：

```bash
AGENT_HOST_TYPE=vscode
AGENT_TEAM_PROJECT_ROOT=/ABS/PATH/TO/ai-agent-dev-system/agent_team_project
```

说明：

- VS Code 属于白名单宿主
- 主 Agent 与子 Agent 均优先使用宿主内置模型

## 5. 首次运行 SOP

### 5.1 验证根入口

在 VS Code Agent Chat 中问：

```text
你是谁？
```

期望：

- 回答自己是主 Agent / 总指挥

### 5.2 验证 custom agent / mode

如果 VS Code 当前版本支持 custom agents / modes：

1. 切到 `main.agent.md` 对应模式
2. 再切到 `frontend.agent.md`、`backend.agent.md`、`test.agent.md`

期望：

- 模式切换后，角色说明与行为边界明显变化

### 5.3 验证 runtime backend（可选）

如果你已接入 runtime backend：

1. 让主 Agent 生成决策
2. 启动 runtime
3. 检查 `agent_team_project/` 下是否生成：
   - `agent_decision.json`
   - `agent_feedback.txt`

## 6. 人工 GUI 走查清单

### 6.1 入口层

- [ ] VS Code 已打开仓库根目录
- [ ] Copilot Chat 已启用
- [ ] 根 `AGENTS.md` 已被当前会话读取
- [ ] `.github/agents/*.agent.md` 可被识别为入口模式

### 6.2 角色层

- [ ] 主 Agent 模式能回答为主 Agent
- [ ] 前端 / 后端 / 测试模式能体现角色边界
- [ ] 切换模式后会引用对应 `agents/*.md`

### 6.3 runtime（可选）

- [ ] 已为运行环境传入 `AGENT_HOST_TYPE=vscode`
- [ ] 已传入 `AGENT_TEAM_PROJECT_ROOT`
- [ ] `agent_decision.json` 可生成
- [ ] `agent_feedback.txt` 可生成

## 7. 常见问题

### 7.1 只看到普通 Chat，看不到 agent/mode

排查：

1. VS Code / Copilot Chat 版本是否支持 custom agents
2. `.github/agents/*.agent.md` 是否在工作区根目录下
3. 是否需要重启 VS Code

### 7.2 主 Agent 没按仓库规则执行

排查：

1. 是否打开了仓库根目录
2. 根 `AGENTS.md` 是否存在
3. 会话是否真的读取到了 `OpenSpec.md`、`global-rules/*.md`

## 8. 参考文档

- `platform-adapters/vscode/README.md`
- `platform-adapters/vscode/agents-entry.md`
- `platform-adapters/vscode/chat-mode-mapping.md`
