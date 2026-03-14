## Generic adapter 概览

`platform-adapters/generic/` 面向第三方 Codex / Agent 插件或自研 Agent 平台，提供一套**与具体产品无关的适配模板**。

当前 V2.2 明确收敛的第三方宿主目标为：

- `Continue`
- `OpenAI-Codex`

目标：

- 让任意具备「调用模型 + 读写文件或调用外部进程」能力的宿主，都可以复用本仓库的治理内核；  
- 不要求宿主采用 Cursor / VS Code 的具体接口，只需满足一组抽象能力。

### 目录结构

- `host-capability-checklist.md`：列出适配本仓库所需的宿主能力清单（decision_sink / runtime_trigger / feedback_bridge / workspace_binding 等）。  
- `adapter-template.md`：为新宿主编写 adapter 文档时可复制的模板。
- `continue.md`：Continue 插件的适配建议。
- `openai-codex.md`：OpenAI-Codex 插件的适配建议。
- `continue-从0开始初始化配置SOP与GUI走查清单.md`：Continue 从 0 开始配置与人工走查手册。
- `openai-codex-从0开始初始化配置SOP与GUI走查清单.md`：OpenAI-Codex 从 0 开始配置与人工走查手册。

> **关于运行后端触发规则**：  
> 第三方宿主在设计「根据用户指令何时触发运行后端」时，不应各自发明一套条件，而是优先遵循根仓库 `AGENTS.md` 中关于「基于 change-id 的智能触发运行后端」的全局约定；本 generic adapter 只负责抽象出 decision_sink / runtime_trigger / feedback_bridge / workspace_binding 能力，并在各宿主具体文档中给出示例接线方式。

## 第三方宿主的模型策略

第三方宿主与白名单宿主的规则不同：

- **主 Agent（当前主会话）**：优先使用宿主内置模型。  
- **子 Agent / 运行后端执行链路**：直接走个人自定义 OpenAI 兼容 API 模型调度策略。  

原因是第三方宿主往往缺少与官方宿主等价的内置多 Agent 调度、规则加载一致性和运行时桥接能力，因此对子 Agent 的默认策略更适合直接落到统一 API 链路。

## 建议的加载顺序规范（V2.4.2）

对于 Continue、OpenAI-Codex 或自研宿主等第三方环境，建议在 adapter 设计时参考以下加载顺序：

1. **simple 任务**  
   - 仅在会话中注入最小入口规则与当前项目的 `AGENTS.md` 等；  
   - 不强制一次性加载完整 `global-rules/projects-rules-for-agent.md` 与 `skills-rules-for-agent.md`，可在需要时按主题加载 `memory/` 条目。

2. **heavy 任务**  
   - 当适配层根据任务或用户指令判定为 heavy 时，应在上下文中追加：  
     - `global-rules/projects-rules-for-agent.md`；  
     - `global-rules/skills-rules-for-agent.md`；  
     - 当前执行方对应的 `agents/*.md`。  
   - 若宿主支持更细致的自动加载，可在进入 heavy 后，再根据 `skills-rules-for-agent.md` 的映射，按需加载对应 `skills/*/SKILL.md` 与少量相关 `memory/*` 条目。

> 适配说明：具体 simple/heavy 判定与加载触发点，可参考 `global-rules/projects-rules-for-agent.md` 第 1.6 节与相关 memory pattern，并结合宿主能力实现；本节仅给出任务分层与规则/记忆加载的大致顺序建议。
