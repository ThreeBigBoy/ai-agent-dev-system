# agent_team_project 说明

## 1. 定位

`agent_team_project/` 是本仓库默认的 **2.0 近全自动闭环运行时 backend**。

它负责：

- 接收总指挥写入的决策文件（优先 `agent_decision.json`，兼容 `cursor_decision.json`）
- 触发执行链路
- 生成反馈文件（优先 `agent_feedback.txt`，兼容 `cursor_feedback.txt`）
- 持久化运行状态与任务结果文件

它**不负责**：

- 定义治理层角色全集
- 定义技能映射权威
- 定义最终日志制度
- 定义最终配额与模型治理规则

这些规则仍以 `OpenSpec.md`、`global-rules/*.md`、`agents/*.md`、`skills-rules-for-agent.md` 为准。

## 2. 默认执行链路

默认链路如下：

1. 主 Agent 通过 MCP `write_decision` 写入决策文件（优先 `agent_decision.json`，兼容 `cursor_decision.json`）
2. `run_skill.py` 读取决策并触发执行
3. `dynamic_agent_skill.py` 承接执行与反馈汇总
4. 结果写入反馈文件（优先 `agent_feedback.txt`，兼容 `cursor_feedback.txt`）
5. 插件监听反馈文件并复制到剪贴板
6. 用户将反馈粘贴回 Chat
7. 主 Agent 再做继续迭代或结束闭环的判断

补充说明：

- 在 **Cursor adapter** 当前实现下，`~/.cursor/mcp.json` 中的 `AGENT_TEAM_PROJECT_ROOT` 应绑定到 `ai-agent-dev-system/agent_team_project`。  
- 其他宿主若复用本 backend，应优先按各自官方文档与 adapter 设计决定运行目录绑定方式，而不是机械复用 Cursor 的路径约束。

## 3. backend scope

当前默认 backend 固定支持以下 5 个 executor：

- 产品经理
- 架构师
- 前端工程师
- 后端工程师
- 测试工程师

说明：

- 这 5 个 executor 是**运行层执行子集**。
- 它们对应治理层中的：产品经理 Agent、架构 Agent、前端 Agent、后端 Agent、测试 Agent。
- 它们**不包含**：主 Agent、文档 Agent、Bug 修复 Agent。

## 4. 与治理层的关系

治理层角色全集固定为：

- 主 Agent
- 产品经理 Agent
- 架构 Agent
- 前端 Agent
- 后端 Agent
- 测试 Agent
- 文档 Agent
- Bug 修复 Agent

关系说明：

- 主 Agent 负责统筹、决策、审核与闭环，不进入默认 backend 的 executor 枚举。
- 文档 Agent、Bug 修复 Agent 是治理层合法角色，但默认不由本 backend 直接调度。
- 若后续需要支持更多 executor，应先在治理层明确角色边界，再扩展本 backend 的 schema 与执行器实现。

## 5. 文件职责

- `agent_team_mcp_server.py`：提供 `write_decision` 等运行侧工具能力
- `run_skill.py`：读取决策并触发执行
- `dynamic_agent_skill.py`：执行默认 5 角色协作链路
- `runtime_config.json`：统一声明 backend 名称、executor 子集、模型调用策略、LLM 参数与运行超时
- `runtime_config.py`：为运行脚本提供统一配置加载入口
- `agent_decision.json` / `cursor_decision.json`：决策文件（新旧命名兼容）
- `agent_feedback.txt` / `cursor_feedback.txt`：执行反馈（新旧命名兼容）
- `agent_state.json`：运行状态
- `task_*.txt`：任务产出快照

## 6. runtime_config.json 字段说明

当前 `runtime_config.json` 主要字段含义如下：

- `backend_name`
  - 标识当前运行时 backend 名称，默认值为 `inline-langgraph`
- `executors`
  - 默认 backend 支持的 5 个 executor 列表
  - 同时被 `agent_team_mcp_server.py` 与 `dynamic_agent_skill.py` 共享
- `model_strategy`
  - 声明模型调用优先级与 fallback 逻辑
  - `preferred_provider`：优先模型提供方，当前为 `cursor_builtin`
  - `fallback_provider`：降级模型提供方，当前为 `api`
  - `cursor_builtin.mode`：当前为 `Auto`
  - `api.models.simple`：简单任务场景使用的 API 模型候选列表
  - `api.models.complex`：中等/复杂任务场景使用的 API 模型候选列表
- `host_policy`
  - 声明宿主白名单与第三方宿主的子 Agent 调度策略
  - `default_host`：未显式传入宿主类型时的默认值，当前为 `cursor`
  - `builtin_preferred_hosts`：子 Agent 维持“宿主内置模型优先”的宿主列表
  - `api_preferred_hosts`：子 Agent 直接走个人 API 模型链路的宿主列表
  - `subagent_provider_policy`：宿主到子 Agent 模型提供方策略的映射
- `llm`
  - 运行时 LLM 的温度、超时等参数
- `run_skill`
  - `run_skill.py` 的超时配置

## 7. 模型调用策略

当前默认策略为：

1. **宿主白名单与第三方宿主区分**
   - 白名单宿主：`cursor`、`vscode`
   - 第三方宿主：`continue`、`openai-codex`
   - 通过环境变量 `AGENT_HOST_TYPE` 传入当前宿主类型，运行后端据此决定子 Agent 的模型链路策略

2. **白名单宿主下，子 Agent 优先使用宿主内置模型**
   - 当前白名单宿主为 Cursor、VS Code 官方 / GitHub Copilot
   - 优先策略为 `cursor_builtin`
   - 默认模式为 Cursor `Auto`
   - 目标是优先走宿主内置模型链路，而不是优先走 `.env` 中 API 模型链路

3. **第三方宿主下，子 Agent 直接走 API 链路**
   - 当前明确支持的第三方宿主为 Continue、OpenAI-Codex
   - 在这些宿主下，主 Agent 可继续使用宿主内置模型，但 `agent_team_project` 承接的子 Agent 执行链路直接使用个人 API 模型候选

4. **若宿主内置模型链路失败，则自动 fallback 到 API 链路**
   - 当前运行时 backend 已支持该降级顺序
   - 个人自定义 API 使用 OpenAI 兼容接口
   - 当前默认通过环境变量接入：
     - `OPENAI_API_BASE_URL=https://api.siliconflow.cn/v1`
     - `OPENAI_API_KEY=<your_key>`
   - 但目前仓库内**尚未接入稳定的 Python -> Cursor 内置模型桥接器**
   - 因此当前实现会先尝试 `cursor_builtin`，随后因“未接入桥接器”自动降级到个人 API 模型候选链路

5. **API 链路模型优先级**
   - `simple` 场景：
     - `Qwen/Qwen3-8B`
     - `Pro/deepseek-ai/DeepSeek-V3.2`
   - `complex` 场景：
     - `Pro/deepseek-ai/DeepSeek-V3.2`
     - `Pro/MiniMaxAI/MiniMax-M2.5`
     - `Pro/moonshotai/Kimi-K2.5`

说明：

- 当前代码会按上述顺序逐个尝试模型候选，直到成功或全部失败。
- 推荐使用策略：
  - 高频轻量任务优先 `Qwen/Qwen3-8B`
  - 核心开发任务优先 `Pro/deepseek-ai/DeepSeek-V3.2`
  - 特殊复杂场景再提升到 `Pro/MiniMaxAI/MiniMax-M2.5`
  - `Pro/moonshotai/Kimi-K2.5` 作为补充可用模型保留，用于特定长文档或中文推理场景
- 后续若补上 Cursor 内置模型桥接器，无需改变治理层规则，只需让 `cursor_builtin` provider 变为可执行实现即可。

## 8. 使用边界

- 本目录是**运行实现**，不是角色规范说明。
- 本目录不得与 `agents/`、`global-rules/`、`OpenSpec.md` 形成平行治理体系。
- 若运行实现与治理层规则冲突，一律以治理层为准。
