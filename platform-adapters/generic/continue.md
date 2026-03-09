## Continue adapter 概览

本文档描述 **Continue 插件** 作为第三方宿主时，如何适配 `ai-agent-dev-system`。

### 1. 宿主定位

- Continue 属于 **第三方宿主**，不在当前白名单宿主范围内。  
- 因此模型策略采用：
  - 主 Agent：优先使用 Continue 宿主内置模型能力
  - 子 Agent / 运行后端：直接走个人自定义 OpenAI 兼容 API 模型调度策略

### 2. 建议接线方式

- `decision_sink`
  - 由 Continue 会话或其可调用脚本 / 命令，把结构化决策写入 `agent_decision.json`
- `runtime_trigger`
  - 通过 Continue 可触发的本地命令或任务，启动 `agent_team_project/run_skill.py`
- `feedback_bridge`
  - 若无法直接把消息回写到 Continue 对话，可采用“反馈文件 + 剪贴板 + 人工粘贴”的降级方案
- `workspace_binding`
  - 建议显式传入：
    - `AGENT_HOST_TYPE=continue`
    - `AGENT_TEAM_PROJECT_ROOT=<runtime_dir>`

### 3. 模型策略

- 主 Agent：优先 Continue 当前宿主内置模型
- 子 Agent：由 `agent_team_project` 按 `AGENT_HOST_TYPE=continue` 识别为第三方宿主，直接走个人 API 模型候选链路
- 当前默认 API 候选策略见：
  - `agent_team_project/runtime_config.json`
  - `agent_team_project/README.md`

### 4. 限制与建议

- Continue 与官方宿主相比，规则自动加载、运行时桥接与多 Agent 协同能力可能存在差异；  
- 因此建议：
  - 治理规则仍由 `OpenSpec.md`、`global-rules/*.md`、`agents/*.md`、`skills/*/SKILL.md` 提供
  - Continue 只承担主会话入口与运行触发
  - 子 Agent 执行链路交由统一 API runtime backend 处理
