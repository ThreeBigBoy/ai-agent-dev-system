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

## 第三方宿主的模型策略

第三方宿主与白名单宿主的规则不同：

- **主 Agent（当前主会话）**：优先使用宿主内置模型。  
- **子 Agent / 运行后端执行链路**：直接走个人自定义 OpenAI 兼容 API 模型调度策略。  

原因是第三方宿主往往缺少与官方宿主等价的内置多 Agent 调度、规则加载一致性和运行时桥接能力，因此对子 Agent 的默认策略更适合直接落到统一 API 链路。
