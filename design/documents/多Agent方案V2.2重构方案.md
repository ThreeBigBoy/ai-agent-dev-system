# 多Agent方案V2.2重构方案

## 1. 文档定位

本文档是 `ai-agent-dev-system` 在 V2.1 基础上的进一步升级方案，目标是将当前“Cursor 优先”的多 Agent 体系升级为“**治理层宿主无关 + 宿主入口按平台保留 + 运行后端可插拔**”的 V2.2 体系。

本文档面向后续详细落地执行，覆盖：

1. 跨宿主改造蓝图 V3
2. `platform-adapters/*/` 跨宿主目录改造方案
3. `mcp.template.json` 模板内容
4. `feedback-bridge.md` 的正式文案
5. 现有哪些文档要删掉或改写 Cursor 专属表述
6. `cursor_decision.json`、`cursor_feedback.txt` 等命名 agent 化及其他待改造项

### 1.1 当前补充约束（2026-03-10）

在进入 V2.2 详细落地时，新增两条当前生效的实现约束：

1. **Cursor adapter 的 MCP 绑定值**
   - 对 Cursor IDE 而言，`~/.cursor/mcp.json` 中 `AGENT_TEAM_PROJECT_ROOT` 的当前实际绑定值应为 `ai-agent-dev-system/agent_team_project`。  
   - 这是 Cursor 当前主流程的实现约束；其他宿主应优先遵循各自官方文档与 adapter 设计。

2. **统一模型策略**
   - 白名单宿主（当前为 Cursor 官方、VS Code 官方 / GitHub Copilot）下，主 Agent 与子 Agent 优先使用宿主内置模型。  
   - 第三方宿主（当前明确为 Continue、OpenAI-Codex）下，主 Agent 优先使用宿主内置模型，但子 Agent / 运行后端直接走个人自定义 OpenAI 兼容 API 模型调度策略。  
   - 若宿主内置模型无响应、异常或不可用，再降级到个人自定义 OpenAI 兼容 API 模型链路。  
   - 当前默认 API 提供方示例为 SiliconFlow，Base URL 为 `https://api.siliconflow.cn/v1`。  
   - 当前推荐模型分工：
     - 高频轻量任务：`Qwen/Qwen3-8B`
     - 核心开发任务：`Pro/deepseek-ai/DeepSeek-V3.2`
     - 特殊复杂场景：`Pro/MiniMaxAI/MiniMax-M2.5`
     - 补充可用模型：`Pro/moonshotai/Kimi-K2.5`

## 2. V2.2 重构背景

### 2.1 V2.1 已解决的问题

V2.1 已完成以下收敛：

- `OpenSpec.md + global-rules/*.md + agents/*.md + skills/*/SKILL.md` 作为治理层唯一权威
- `agent_team_project/` 降级为默认运行后端
- `.cursor/rules/agent.mdc` 降级为 Cursor 入口规则
- 日志口径统一到项目级 `design/documents/迭代日志.md`
- 默认 backend 的 5 个 executor 与治理层角色全集完成区分

### 2.2 V2.2 要解决的新问题

如果目标从“服务 Cursor Agent Chat”扩展为“同时适用于 Cursor IDE、VS Code 官方 Agent Chat、其他第三方插件类 Agent Chat”，则当前仓库仍存在如下问题：

1. 治理层中仍保留大量 Cursor 专属前提，如 `.cursor/rules/`、`.cursorrules`、Cursor Pro、Composer、Kimi、Auto、Ctrl+Shift+A、`cursor_decision.json` 等。
2. 宿主入口与宿主专属运行链路尚未结构化沉淀，导致 Cursor 实现细节仍然像“主方案”，而不是“一个 adapter”。
3. `agent_team_project/` 的文件命名与反馈链路明显带有 Cursor 品牌痕迹，不利于未来 VS Code 与第三方插件复用。
4. `~/.cursor/mcp.json` 与自定义插件机制尚未被定义为“Cursor adapter 的宿主接线层”，而仍然容易被误解为方案本体。

### 2.3 V2.2 总结论

V2.2 不应把 Cursor 的入口文件从根目录移走；应采用以下原则：

- **治理内核继续放在仓库通用层**
- **宿主专属入口文件继续保留在宿主要求的位置**
- **宿主专属厚内容下沉到 `platform-adapters/<host>/`**
- **运行链路抽象成宿主无关协议**
- **Cursor 作为首个完整落地 adapter 保留**

## 3. 跨宿主改造蓝图 V3

### 3.1 目标架构

V3 架构建议拆为四层：

1. **治理内核层**
   - 作用：定义变更机制、角色边界、技能触发、日志制度、审核与闭环规则
   - 文件：`OpenSpec.md`、`global-rules/`、`agents/`、`skills/`
   - 要求：宿主无关，不直接绑定 Cursor / VS Code / 第三方插件

2. **宿主适配层**
   - 作用：解释不同宿主如何加载入口规则、如何注入角色、如何触发运行链路、如何接收反馈
   - 目录：`platform-adapters/cursor/`、`platform-adapters/vscode/`、`platform-adapters/generic/`
   - 要求：只写宿主适配差异，不改治理规则

3. **宿主入口层**
   - 作用：保留在宿主要求的位置，让宿主可以直接发现和加载规则
   - Cursor：`.cursor/rules/*.mdc`
   - VS Code：根 `AGENTS.md`、`.github/agents/*.agent.md`
   - 第三方插件：按插件要求位置保留最薄入口文件
   - 要求：这些文件仅做“加载壳”，不再堆厚制度正文

4. **运行后端层**
   - 作用：承接决策写入、执行、反馈、状态持久化
   - 当前默认实现：`agent_team_project/`
   - 后续可扩展：`skills-subagent`、`event-bus-runtime`、`mcp-runtime`

### 3.2 权威优先级

V2.2 中统一优先级如下：

1. `OpenSpec.md`
2. `global-rules/*.md`
3. `agents/*.md`
4. `skills/*/SKILL.md`
5. `platform-adapters/*/*.md`
6. 宿主入口文件（如 `.cursor/rules/*.mdc`、`AGENTS.md`、`.github/agents/*.agent.md`）
7. 运行后端实现（如 `agent_team_project/`）
8. 用户本机配置（如 `~/.cursor/mcp.json`、插件设置、快捷键设置）

说明：

- 宿主入口文件是“加载入口”，不是治理权威源。
- 用户本机配置是“接线层”，不应成为规则来源。
- 运行后端不得改写治理层角色和日志制度。

### 3.3 宿主无关运行协议

V2.2 建议把现有 Cursor 2.0 闭环抽象成四个宿主无关接口：

1. `decision_sink`
   - 用途：接收主 Agent 的结构化决策对象
   - Cursor 当前实现：MCP `write_decision` -> `cursor_decision.json`

2. `runtime_trigger`
   - 用途：触发运行后端开始执行
   - Cursor 当前实现：快捷键 / 宏命令 `Ctrl+Shift+A`

3. `feedback_bridge`
   - 用途：把运行结果送回 Chat
   - Cursor 当前实现：监听反馈文件 -> 复制剪贴板 -> 用户粘贴

4. `workspace_binding`
   - 用途：告诉运行层当前宿主下应绑定到哪个运行目录或工作目录
   - Cursor 当前实现：`AGENT_TEAM_PROJECT_ROOT`，当前实际绑定到 `ai-agent-dev-system/agent_team_project`

后续 VS Code / 第三方插件只需各自实现这四类能力，不需要重写治理体系。

## 4. platform-adapters/*/ 跨宿主目录改造方案

### 4.1 目标目录结构

建议新增如下目录：

```text
platform-adapters/
├── README.md
├── cursor/
│   ├── README.md
│   ├── rule-loading.md
│   ├── mcp-setup.md
│   ├── feedback-bridge.md
│   ├── runtime-integration.md
│   ├── mcp.template.json
│   └── extension/
│       └── README.md
├── vscode/
│   ├── README.md
│   ├── agents-entry.md
│   ├── chat-mode-mapping.md
│   └── feedback-bridge.md
└── generic/
    ├── README.md
    ├── host-capability-checklist.md
    └── adapter-template.md
```

### 4.2 `platform-adapters/README.md`

职责：

- 说明什么是“宿主适配层”
- 解释治理内核、宿主入口、运行后端三者的关系
- 列出当前支持状态：
  - `cursor/`：已完整落地
  - `vscode/`：规划中
  - `generic/`：抽象模板

### 4.3 `platform-adapters/cursor/`

职责：

- 统一存放所有 Cursor 专属设计说明
- 不替代 `.cursor/rules/` 的真实加载位置
- 文档化 MCP 接线与插件反馈桥接

#### 应保留在根目录的位置

- `.cursor/rules/*.mdc`

原因：

- Cursor IDE 只有在工作区根目录 `.cursor/` 下才能直接发现并加载 `.mdc`
- 因此 `.cursor/rules/` 不能物理迁走
- 但其内容应变薄，只做入口与跳转

#### 应迁入 `platform-adapters/cursor/` 的厚内容

- Cursor 规则加载说明
- `~/.cursor/mcp.json` 注册 `agent-team` 的说明
- 插件监听反馈文件并复制剪贴板的说明
- 快捷键触发执行链路说明
- Cursor 宿主限制与降级方案说明

### 4.4 `platform-adapters/vscode/`

职责：

- 说明 VS Code 官方 Agent Chat 的入口文件和映射方式
- 定义如何通过根 `AGENTS.md` 与 `.github/agents/*.agent.md` 适配本仓库

建议拆分：

- `README.md`
  - 说明 VS Code adapter 的总体定位
- `agents-entry.md`
  - 说明根 `AGENTS.md` 的职责、加载方式、内容边界
- `chat-mode-mapping.md`
  - 说明 `.github/agents/*.agent.md` 如何映射主 Agent / 子 Agent
- `feedback-bridge.md`
  - 说明 VS Code 是否支持自动回写 Chat；若不支持，如何做降级

### 4.5 `platform-adapters/generic/`

职责：

- 供第三方 Codex / Agent 插件复用
- 不绑定具体产品，给出最低适配要求

建议拆分：

- `README.md`
  - 解释 generic adapter 适用场景
- `host-capability-checklist.md`
  - 判断某插件是否具备 `decision_sink`、`runtime_trigger`、`feedback_bridge`、`workspace_binding`
- `adapter-template.md`
  - 提供新的宿主 adapter 编写模板

## 5. 各宿主入口文件的处理原则

### 5.1 Cursor

保留：

- `.cursor/rules/agent.mdc`
- `.cursor/rules/global-rules.mdc`

要求：

- 继续放在仓库根目录
- 继续供 Cursor 自动加载
- 内容改为“最薄入口”

### 5.2 VS Code

新增：

- 根目录 `AGENTS.md`
- `.github/agents/main.agent.md`
- `.github/agents/frontend.agent.md`
- `.github/agents/backend.agent.md`
- `.github/agents/test.agent.md`

要求：

- `AGENTS.md` 作为 VS Code 官方 Agent Chat 的 always-on instructions 入口
- `.github/agents/*.agent.md` 作为自定义 agent / mode 的轻量入口
- 不把完整治理制度复制到这些文件中

### 5.3 第三方插件

原则：

- 优先复用根 `AGENTS.md`
- 若插件支持独立 agent 文件，则按该插件规范新增最薄入口
- 详细规则仍回指治理层和 `platform-adapters/generic/`

## 6. `mcp.template.json` 模板内容

V2.2 建议不再把真实 `~/.cursor/mcp.json` 当主说明源，而是在仓库内提供模板文件：

路径建议：

- `platform-adapters/cursor/mcp.template.json`

模板内容如下：

```json
{
  "mcpServers": {
    "agent-team": {
      "command": "python3",
      "args": [
        "/ABS/PATH/TO/ai-agent-dev-system/agent_team_project/agent_team_mcp_server.py"
      ],
      "env": {
        "AGENT_TEAM_PROJECT_ROOT": "/ABS/PATH/TO/ai-agent-dev-system/agent_team_project"
      }
    }
  }
}
```

### 6.1 模板说明

- `command`
  - 当前默认使用 `python3`
- `args`
  - 指向仓库中的 `agent_team_project/agent_team_mcp_server.py`
- `AGENT_TEAM_PROJECT_ROOT`
  - 对 Cursor adapter 而言，当前实际绑定值为 `ai-agent-dev-system/agent_team_project`
  - 其他宿主请优先按各自官方文档和 adapter 方案执行，不要求复用这一绑定值

### 6.2 配套文案

`platform-adapters/cursor/mcp-setup.md` 应明确说明：

1. `agent-team` 是 Cursor adapter 的 `decision_sink` 实现
2. `write_decision` 只是当前 Cursor 方案的写入方式
3. 未来其他宿主可以用不同的 sink 实现同一协议

## 7. `feedback-bridge.md` 的正式文案

建议在 `platform-adapters/cursor/feedback-bridge.md` 中使用如下正式文案：

```md
# Cursor Feedback Bridge

## 1. 定位

本机制是 `ai-agent-dev-system` 在 Cursor 宿主下的反馈桥接实现，用于把运行后端生成的执行反馈重新送回 Cursor Chat。

它属于 Cursor adapter 的宿主接线层，不属于治理规则本身。

## 2. 当前实现

当前 Cursor 宿主下的反馈桥接采用降级方案：

1. 运行后端执行完成后，将反馈写入反馈文件。
2. 自定义插件监听反馈文件变化。
3. 插件读取反馈内容后复制到系统剪贴板。
4. 插件弹窗提示用户将反馈粘贴回 Chat。
5. 用户在 Chat 中粘贴并发送后，主 Agent 继续判断“重新分工”或“结束闭环”。

## 3. 为什么需要该方案

原因不是治理层要求人工参与，而是 Cursor 当前未公开“由扩展程序直接向 Chat 注入消息”的稳定 API。

因此：

- 从运行后端到反馈文件的链路是自动的
- 从反馈文件到剪贴板的链路是自动的
- 从剪贴板到 Chat 的最后一步需要用户粘贴一次

这属于 Cursor 当前宿主能力限制下的降级补丁。

## 4. 边界

- 本机制不改变治理层规则
- 本机制不改变主 Agent 的决策逻辑
- 本机制仅是 Cursor 下的 `feedback_bridge` 实现
- 若未来 Cursor 开放扩展直接回写 Chat 的能力，可用新的 bridge 实现替代本方案

## 5. 与其他宿主的关系

- VS Code adapter 可以使用不同的 feedback bridge
- 第三方插件 adapter 也可以采用不同桥接方式
- 所有宿主都只需满足“运行结果能够回到主 Agent”这一抽象要求
```

## 8. `cursor_decision.json`、`cursor_feedback.txt` 命名抽象 agent 化方案

### 8.1 当前问题

当前命名显式绑定 Cursor：

- `cursor_decision.json`
- `cursor_feedback.txt`

这会导致：

- VS Code / 第三方插件复用时语义不自然
- 宿主无关协议难以建立

### 8.2 V2.2 建议命名

建议抽象为宿主无关命名：

- `agent_decision.json`
- `agent_feedback.txt`

如果后续要继续拆分宿主无关状态文件，还可补充：

- `agent_runtime_state.json`
- `agent_task_*.txt`

### 8.3 兼容迁移策略

V2.2 不建议一次性硬切，建议两阶段迁移：

1. **第一阶段：双命名兼容**
   - 代码优先读新名字
   - 找不到时回退读旧名字
   - 输出时同时写新名字，必要时镜像写旧名字

2. **第二阶段：文档统一收口**
   - 所有文档统一改写为 agent 化命名
   - Cursor adapter 文档中说明旧名字仅为兼容层

## 9. 其他待改造项

### 9.1 模型策略去 Cursor 品牌化

当前治理层大量出现：

- Cursor Pro
- Composer
- Kimi
- Auto

V2.2 建议抽象为能力等级：

- `host_builtin_primary`
- `long_context_reasoning`
- `lightweight_low_cost`
- `external_review_model`

然后在各宿主 adapter 中做映射：

- Cursor adapter：映射到 Composer / Kimi / Auto / external API
- VS Code adapter：映射到该宿主可用模型
- generic adapter：由宿主自行填充

### 9.2 `AGENT_TEAM_PROJECT_ROOT` 语义统一

当前该环境变量在描述上容易混淆“仓库根目录”和“runtime backend 目录”。

V2.2 应统一定义为：

- 当前执行任务所属的**项目工作区根目录**

同时更新：

- `agent_team_mcp_server.py` 注释
- `mcp.template.json`
- Cursor adapter 说明文档

### 9.3 运行链路术语统一

当前文档中的术语混杂：

- 主 Agent
- 总指挥
- Cursor Chat
- write_decision
- 插件复制剪贴板

V2.2 应拆为：

- 治理术语：主 Agent、子 Agent、Skill、change-id
- 协议术语：`decision_sink`、`runtime_trigger`、`feedback_bridge`、`workspace_binding`
- 宿主术语：Cursor、VS Code、第三方插件

## 10. 需要删掉或改写 Cursor 专属表述的现有文档

以下文件应纳入 V2.2 改造范围。

### 10.1 必改

1. `README.md`
   - 现状：仍把 AI 协作入口默认指向 `.cursor/rules/`
   - 改法：改为“宿主入口由各平台 adapter 提供”，Cursor 只是当前完整落地宿主

2. `OpenSpec.md`
   - 现状：多处写“只有被 Cursor 加载为规则时才生效”
   - 改法：改为“只有被宿主入口层正确加载时才生效”，Cursor 作为其中一个例子

3. `global-rules/README.md`
   - 现状：基本全部围绕 Cursor Rules 加载路径解释
   - 改法：拆成
     - 通用说明
     - `platform-adapters/cursor/` 引用

4. `global-rules/projects-rules-for-agent.md`
   - 现状：大量绑定 Cursor Pro、Composer、Kimi、Auto、`.cursorrules`
   - 改法：治理层去品牌化，把宿主专属模型策略和入口策略迁到 adapter 层

5. `agents/主Agent.md`
   - 现状：写死“由 Cursor Chat 当前会话直接承担”
   - 改法：改为“由当前宿主会话承担”，Cursor 作为适配示例放到 adapter 文档

6. `agents/README.md`
   - 现状：有“与 Cursor Settings 里 Subagent 的区别”专章
   - 改法：改为“与宿主原生多 Agent / Subagent 机制的关系”，Cursor 只是示例

7. `.cursor/rules/agent.mdc`
   - 现状：仍承担较多 Cursor 专属运行链路说明
   - 改法：继续瘦身，只保留 Cursor 可加载的最薄入口

8. `agent_team_project/README.md`
   - 现状：直接把 Cursor 方案写成默认运行链路
   - 改法：拆出宿主无关 runtime 协议说明，再把 Cursor 实现细节迁到 `platform-adapters/cursor/`

### 10.2 建议改

1. `tools/cursor-usage-to-iteration-log/README.md`
   - 改法：明确其为 Cursor provider，不是通用模型记录能力

2. `tools/cursor-usage-to-iteration-log/设计-方案与自检/*`
   - 改法：全部归入 Cursor adapter 辅助工具说明，避免被误解为通用层

3. `know-how/规范体系总览.md`
   - 改法：把 `.cursor/rules/` 从“全局入口唯一形态”改为“Cursor 入口实现之一”

4. `know-how/agent-execution-simulation-and-reflection.md`
   - 改法：把 `.cursorrules`、Cursor 规则加载相关表述降级为宿主案例

### 10.3 新增文件

V2.2 建议新增：

- `platform-adapters/README.md`
- `platform-adapters/cursor/README.md`
- `platform-adapters/cursor/rule-loading.md`
- `platform-adapters/cursor/mcp-setup.md`
- `platform-adapters/cursor/feedback-bridge.md`
- `platform-adapters/cursor/runtime-integration.md`
- `platform-adapters/cursor/mcp.template.json`
- `platform-adapters/vscode/README.md`
- `platform-adapters/vscode/agents-entry.md`
- `platform-adapters/vscode/chat-mode-mapping.md`
- `platform-adapters/vscode/feedback-bridge.md`
- `platform-adapters/generic/README.md`
- `platform-adapters/generic/host-capability-checklist.md`
- `platform-adapters/generic/adapter-template.md`
- 根 `AGENTS.md`
- `.github/agents/main.agent.md`

## 11. V2.2 落地执行顺序

### 第一阶段：文档分层

1. 新建 `platform-adapters/` 全目录
2. 新建根 `AGENTS.md`
3. 新建 `.github/agents/` 的 VS Code 入口文件
4. 瘦身 `.cursor/rules/*.mdc`
5. 改写根 `README.md`

### 第二阶段：治理层去 Cursor 品牌化

1. 改写 `global-rules/projects-rules-for-agent.md`
2. 改写 `agents/主Agent.md`
3. 改写 `agents/README.md`
4. 改写 `OpenSpec.md` 中与宿主加载绑定的说明

### 第三阶段：运行协议抽象

1. 在 `agent_team_project/` 中引入 agent 化文件命名兼容层
2. 抽象 `decision_sink`、`runtime_trigger`、`feedback_bridge`、`workspace_binding`
3. 保留 Cursor 当前链路作为第一个完整 adapter

### 第四阶段：Cursor adapter 收口

1. 把 `~/.cursor/mcp.json` 的说明迁到仓库内模板与文档
2. 把插件反馈桥说明迁到 `platform-adapters/cursor/`
3. 将 Cursor 专属模型记录工具降级为 adapter 工具

## 12. 验收标准

V2.2 落地完成后，应满足以下条件：

1. 治理层文档不再把 Cursor 当默认唯一宿主
2. Cursor、VS Code、generic 三类 adapter 都有明确目录与职责
3. `.cursor/rules/` 继续保留在根目录，但只承担 Cursor 入口壳职责
4. 根 `AGENTS.md` 与 `.github/agents/*.agent.md` 建立 VS Code 入口能力
5. `agent_team_project/` 的核心术语和文件命名不再只服务 Cursor
6. `~/.cursor/mcp.json` 与插件监听机制被清楚归类为 Cursor adapter 的宿主接线层
7. V2.1 的治理内核不被破坏，只增加宿主解耦能力

## 13. 一句话结论

V2.2 的核心不是“把 Cursor 方案删掉”，而是**把 Cursor 从“默认世界观”降级为“第一个完整落地的宿主 adapter”**。  
治理内核继续稳定，宿主入口各归其位，运行协议抽象统一，之后 VS Code 与第三方插件才能真正平滑接入。
