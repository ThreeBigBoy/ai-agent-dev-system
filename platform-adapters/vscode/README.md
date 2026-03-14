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

> **关于运行后端触发规则**：  
> VS Code 下「根据用户指令何时触发运行后端」的智能行为（如检测到 change-id + 变更推进类关键词时按 heavy + 运行后端执行），应直接复用根仓库 `AGENTS.md` 中的结论级约定；本 adapter 只需说明 VS Code 如何接线 decision_sink / runtime_trigger / feedback_bridge，不在本层重复定义触发条件。

## 默认加载顺序规范（V2.4.2 建议）

当 VS Code Agent Chat 或相关插件在本仓库中工作时，推荐遵循与 Cursor 一致的「rules → SKILL/memory」渐进式加载顺序：

1. **simple 任务**  
   - 仅注入根级 `AGENTS.md` 与必要的入口规则（对应 `.cursor/rules/*.mdc` 在 Cursor 下的职责）；  
   - 不强制一次性加载完整 `global-rules/projects-rules-for-agent.md` 与 `skills-rules-for-agent.md`，必要时按主题少量加载 `memory/` 条目。

2. **heavy 任务**  
   - 当 simple/heavy 判定结果为 heavy 时，应在 Agent 上下文中显式加载：  
     - `global-rules/projects-rules-for-agent.md`；  
     - `global-rules/skills-rules-for-agent.md`；  
     - 当前执行方对应的 `agents/*.md`。  
   - 需要具体执行步骤或模版时，再根据 `skills-rules-for-agent.md` 指定的技能路径，加载 `skills/*/SKILL.md` 与少量相关 `memory/*` 条目。

> 说明：本节为 adapter 层建议，不改变治理内核规则的优先级；如 VS Code 官方能力发生变化，可在不违反 OpenSpec 与 global-rules 的前提下调整实现细节。
