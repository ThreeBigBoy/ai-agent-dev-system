# OpenAI-Codex 从 0 开始初始化配置 SOP 与 GUI 走查清单

## 1. 适用对象

适用于首次从 Git 下载 `ai-agent-dev-system`，希望在 **OpenAI-Codex 插件** 中使用多 Agent 协同系统的用户。

## 2. 目标结果

完成本手册后，应达到以下状态：

1. OpenAI-Codex 主会话可读取仓库治理规则
2. 主 Agent 在宿主侧可正常工作
3. 第三方宿主策略生效：主 Agent 用宿主内置模型，子 Agent **也优先用宿主内置模型**（仅在宿主内置模型不可用时降级到个人 API 模型链路）
4. runtime backend 可通过 `AGENT_HOST_TYPE=openai-codex` 正常执行

## 3. 前置条件

- 已安装支持 OpenAI-Codex 插件的 IDE 宿主
- 已安装 OpenAI-Codex 插件
- 已将本仓库克隆到本机
- 已安装 Python 3

## 4. 初始化配置 SOP

### 4.1 打开仓库根目录

打开：

- `ai-agent-dev-system/`

### 4.2 安装 runtime 依赖

在仓库根目录执行：

```bash
pip3 install mcp jsonschema python-dotenv langchain-openai langgraph pydantic
```

### 4.3 准备个人 API 环境变量

OpenAI-Codex 属于第三方宿主，但当前配置下主 Agent 与子 Agent 均**优先使用宿主内置模型**；  
当宿主内置模型不可用或需要 fallback 时，才会走个人 API 模型链路，因此仍需准备 API 凭据：

```env
OPENAI_API_KEY=your_key
OPENAI_API_BASE_URL=https://api.siliconflow.cn/v1
```

### 4.4 配置主会话

目标是让 OpenAI-Codex 当前主会话：

1. 读取根 `AGENTS.md`
2. 能访问：
   - `OpenSpec.md`
   - `global-rules/*.md`
   - `agents/*.md`
   - `skills/*/SKILL.md`

### 4.5 接入 runtime backend

触发 runtime backend 时，显式传入：

```bash
AGENT_HOST_TYPE=openai-codex
AGENT_TEAM_PROJECT_ROOT=/ABS/PATH/TO/ai-agent-dev-system/agent_team_project
```

说明：

- `openai-codex` 会被 runtime 识别为第三方宿主
- 子 Agent 在当前配置下**优先使用宿主内置模型**，仅在宿主不可用时走个人 API 模型候选链路

## 5. 首次运行 SOP

### 5.1 验证主 Agent 入口

在 OpenAI-Codex 会话中问：

```text
你是谁？
```

期望：

- 回答为主 Agent / 总指挥

### 5.2 验证策略分流

让主 Agent 生成一个简单决策并触发 runtime。

期望：

- 主会话仍在宿主内运行（主 Agent 用宿主内置模型）
- 子 Agent 执行链路**优先使用宿主内置模型**，仅在宿主不可用时才会降级到 API 模型候选

### 5.3 验证文件链路

期望生成：

- `agent_team_project/agent_decision.json`
- `agent_team_project/agent_feedback.txt`

## 6. 人工 GUI 走查清单

- [ ] OpenAI-Codex 插件已启用
- [ ] 工作区根目录是 `ai-agent-dev-system`
- [ ] 主会话能读取根 `AGENTS.md`
- [ ] 主 Agent 能按治理规则回答
- [ ] 运行时传入了 `AGENT_HOST_TYPE=openai-codex`
- [ ] 运行时传入了 `AGENT_TEAM_PROJECT_ROOT`
- [ ] `agent_decision.json` 已生成
- [ ] `agent_feedback.txt` 已生成

## 7. 常见问题

### 7.1 主会话没按主 Agent 规则工作

排查：

1. 当前插件会话是否能访问仓库根目录内容
2. 是否显式要求读取根 `AGENTS.md`
3. 是否能访问 `OpenSpec.md` 和 `global-rules/*.md`

### 7.2 runtime 无法执行

排查：

1. 是否安装了 Python 依赖
2. 是否传入 `AGENT_HOST_TYPE=openai-codex`
3. 是否传入 `AGENT_TEAM_PROJECT_ROOT`
4. `.env` 中的 API 凭据是否有效

## 8. 参考文档

- `platform-adapters/generic/openai-codex.md`
- `platform-adapters/generic/README.md`
