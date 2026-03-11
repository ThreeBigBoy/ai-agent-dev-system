## OpenAI-Codex adapter 概览

本文档描述 **OpenAI-Codex 插件** 作为第三方宿主时，如何适配 `ai-agent-dev-system`。

### 1. 宿主定位

- OpenAI-Codex 属于 **第三方宿主**，不在当前白名单宿主范围内。  
- 因此模型策略采用：
  - 主 Agent：优先使用 OpenAI-Codex 宿主内置模型能力
  - 子 Agent / 运行后端：**也优先使用 OpenAI-Codex 宿主内置模型能力**，仅在宿主内置模型不可用时再降级到个人自定义 OpenAI 兼容 API 模型调度策略

### 2. 建议接线方式

- `decision_sink`
  - 由宿主会话、命令或外围脚本将结构化决策写入 `agent_decision.json`
- `runtime_trigger`
  - 通过插件支持的命令或任务机制触发 `agent_team_project/run_skill.py`
- `feedback_bridge`
  - 若宿主无法直接向对话写回结果，可使用“反馈文件 + 提示 + 人工粘贴”的降级方案
- `workspace_binding`
  - 建议显式传入：
    - `AGENT_HOST_TYPE=openai-codex`
    - `AGENT_TEAM_PROJECT_ROOT=<runtime_dir>`

### 3. 模型策略

- 主 Agent：优先使用宿主内置模型
- 子 Agent：由 `agent_team_project` 按 `AGENT_HOST_TYPE=openai-codex` 识别为第三方宿主，但**子 Agent 也优先使用宿主内置模型**，仅当宿主内置模型链路不可用或失败时，才走个人 API 模型候选链路
- 当前默认 API 候选策略见：
  - `agent_team_project/runtime_config.json`
  - `agent_team_project/README.md`

### 4. 限制与建议

- OpenAI-Codex 作为第三方宿主，其入口规则加载、反馈回传与运行触发能力可能与官方宿主不同；  
- 因此建议：
  - 治理层文档保持宿主无关
  - 宿主层只负责主会话入口和运行触发
  - 子 Agent 统一交给 runtime backend 的 API 链路执行
