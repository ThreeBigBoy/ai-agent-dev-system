## VS Code adapter 概览

`platform-adapters/vscode/` 描述 **ai-agent-dev-system 在 VS Code 官方 Agent Chat / 相关插件下的适配方式**。

核心目标：

- 利用 VS Code 提供的 Agent 入口（如根 `AGENTS.md`、`.github/agents/*.agent.md` 等），把治理内核规则注入到 Agent 会话；  
- 定义 VS Code 宿主下的 `decision_sink` / `runtime_trigger` / `feedback_bridge` / `workspace_binding` 实现思路。

### 目录结构

- `agents-entry.md`：说明根 `AGENTS.md` 与 `.github/agents/*.agent.md` 在 VS Code 中的职责与边界。  
- `chat-mode-mapping.md`：说明 VS Code 自带/自定义 Agent 模式如何映射到本仓库中的主 Agent与子 Agent 角色。  
- `feedback-bridge.md`：说明在 VS Code 下如何把运行后端反馈回写到 Agent 对话中（或在缺乏 API 时采用的降级方案）。
- `从0开始初始化配置SOP与GUI走查清单.md`：新用户从 Git 下载仓库后，在 VS Code 中完成初始化配置与人工走查的操作手册。

### 当前落地状态

- 已落地根级 `AGENTS.md`，可作为 always-on instructions 入口。  
- 已补齐 `.github/agents/` 下的典型入口骨架：
  - `.github/agents/main.agent.md`
  - `.github/agents/frontend.agent.md`
  - `.github/agents/backend.agent.md`
  - `.github/agents/test.agent.md`
- 这些文件只做 VS Code 宿主入口壳，不替代治理内核文档。
- VS Code 官方宿主属于白名单宿主：
  - 主 Agent 与子 Agent 均优先使用宿主内置模型；
  - 若宿主内置模型无响应、异常或不可用，再降级到个人自定义 OpenAI 兼容 API 模型链路。
- 若 VS Code 侧需要触发运行后端，建议向运行环境显式传入 `AGENT_HOST_TYPE=vscode`。

> 具体 VS Code API 与配置方式可能随版本演进，本目录更关注「职责与抽象」，实现细节可按实际版本更新。
