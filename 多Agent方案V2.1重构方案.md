# 多Agent方案V2.1重构方案

## 1. 文档定位

本文档用于汇总：

1. `ai-agent-dev-system` 当前“总指挥体系 + OpenSpec治理体系 + agent_team_project运行体系”的冲突点与V2.1重构目标。
2. “重构蓝图V2”的正式化版本。
3. 可直接执行的“落地改造清单”，细化到每个关键文件该删哪段、保留哪段、补哪段。

本文档同时对齐以下方案源文档与参考文档：

- `agents/Reference/主Agent-总指挥入口模板-参考.md`
- `otherDocuments/【方案】Cursor 多Agent协同2.0(真协同)/基于Cursor的多Agent全自动协同闭环落地方案（优先插件无缝交互）.md`
- `otherDocuments/【方案】Cursor 多Agent协同2.0(真协同)/基于Cursor的多Agent全自动协同闭环流程图（含文字说明）.md`

## 2. 当前问题归纳

### 2.1 本质问题

当前系统不是“单点规则写错”，而是三层内容发生了叠加：

1. `agent_team_project/` 保留了 2.0 原始“近全自动闭环执行内核”。
2. `OpenSpec.md + global-rules/*.md + agents/*.md + skills/*/SKILL.md` 演进成“治理宪法体系”。
3. `.cursor/rules/agent.mdc` 试图同时承担“总指挥入口 + 治理说明 + 运行链路说明”三种职责。

结果是：

- 规则优先级不够清晰。
- 角色范围出现双套定义。
- 日志口径不统一。
- 模型调度同时存在“治理策略”和“运行硬编码”。
- `agent_team_project` 的定位既像“运行后端”，又被读成“总规范来源”。

### 2.2 V2.1 重构结论

V2.1 不推翻 2.0 主链路，而是做“分层归位”：

1. 保留 `agent_team_project` 作为默认运行时后端。
2. 让 `OpenSpec + global-rules + agents + skills` 成为唯一治理层。
3. 让 `.cursor/rules/agent.mdc` 仅做总指挥入口和优先级声明。
4. 统一日志、角色范围、模型配置来源，消除多头定义。

## 3. 重构蓝图V2.1

### 3.1 总体目标

目标架构拆为三层：

1. 宪法治理层  
   负责：变更入口、change-id、日志、技能触发、审核闭环、配额原则。  
   权威文件：`OpenSpec.md`、`global-rules/projects-rules-for-agent.md`、`global-rules/skills-rules-for-agent.md`

2. 角色治理层  
   负责：主 Agent/子 Agent 的职责边界、审核关系、模型使用边界、协同约束。  
   权威文件：`agents/主Agent.md`、`agents/子Agent-*.md`、`agents/README.md`

3. 运行实现层  
   负责：决策落盘、快捷键触发、执行、反馈、状态持久化。  
   默认后端：`agent_team_project/`

### 3.2 权威优先级

统一优先级如下：

1. `OpenSpec.md`
2. `global-rules/*.md`
3. `agents/*.md`
4. `skills/*/SKILL.md`
5. `.cursor/rules/*.md`
6. `agent_team_project/` 运行实现

约束解释：

- 运行实现不得覆盖治理规则。
- `.cursor/rules/agent.mdc` 只能引用和转述上位规则，不能再自建一套平行制度。
- `agent_team_project` 仅是“默认执行后端”，不再被描述为角色规范或治理规则的权威来源。

### 3.3 `agent_team_project` 的正式定位

V2.1 中将 `agent_team_project/` 定位为：

- 2.0 近全自动闭环运行后端
- 默认 backend：`inline-langgraph`
- 仅覆盖 5 个执行角色：
  - 产品经理
  - 架构师
  - 前端工程师
  - 后端工程师
  - 测试工程师

不纳入其 `executor` 枚举的角色：

- 主 Agent
- 文档 Agent
- Bug 修复 Agent

这些角色仍属于治理体系中的合法角色，但不进入 `cursor_decision.json` 的默认执行枚举。

### 3.4 主 Agent 的正式定位

V2.1 中主 Agent 的角色定义为：

- 默认统筹者
- 决策与分工者
- 审核与闭环推动者
- 运行后端选择者

明确边界：

- 主 Agent 默认不直接执行具体技能。
- 主 Agent 默认不进入 `cursor_decision.json.task_list.executor`。
- 主 Agent 可调用或选择某运行后端，但不替代运行后端实现细节。

### 3.5 日志口径统一

V2.1 建议统一采用项目级单一日志文件：

- `design/documents/迭代日志.md`

记录中必须包含：

- 时间
- change-id
- Agent
- 技能
- 任务
- 输出
- 使用模型

不再把“每个 change-id 自己有一个独立迭代日志文件”作为主口径。  
`design/documents/[change-id]/records/` 继续保留给：

- 验收记录
- 代码评审记录
- 对齐结论
- 复盘/反思

### 3.6 模型策略统一

V2.1 中模型策略做双层拆分：

1. 治理层定义“原则”
   - 哪些角色禁止高成本模型
   - 哪些场景建议 Composer/Kimi/轻量模型
   - 哪些高风险任务建议外部复核

2. 运行层定义“默认实现配置”
   - `agent_team_project` 不再在代码里硬编码模型名
   - 由配置文件统一声明模型调用策略、fallback 顺序、executor 列表、base_url、timeout
   - 当前运行策略为：**优先 Cursor 内置模型（Auto）-> 失败后 fallback 到 API 模型链路**
   - API 模型默认候选为：
     - `simple`：`Qwen/Qwen3-8B` -> `Qwen/Qwen3.5-4B`
     - `complex`：`Pro/deepseek-ai/DeepSeek-V3.2` -> `Pro/MiniMaxAI/MiniMax-M2.5`
   - 当前仓库尚未实现稳定的 Python -> Cursor 内置模型桥接，因此代码层现状为“先尝试 Cursor builtin provider，再自动降级到 API provider”

### 3.7 后续扩展方向

V2.1 只做分层与归位，不强制切换运行后端。后续可扩展为双 backend：

- `inline-langgraph`：当前 `agent_team_project` 方案
- `skills-subagent`：未来严格对齐“子 Agent + SKILL + Cursor Subagent/MCP”的执行后端

这两种 backend 都受同一治理层约束。

## 4. 落地改造清单

以下清单按“文件 -> 删哪段 / 保留哪段 / 补哪段”组织。

---

## 4.1 `.cursor/rules/agent.mdc`

### 目标

从“总指挥制度大总汇”改为“总指挥入口规则”。

### 保留

- 默认身份为总指挥/主 Agent 的入口约定
- 使用 `write_decision` 的主方案
- 收到反馈后继续决策或结束闭环的总流程
- “如与 OpenSpec/global-rules 冲突，则以上位规则为准”的优先级原则

### 删除

- 详细重复 `projects-rules-for-agent.md` 的执行方、SKILL、自检、迭代日志制度
- 与 `主Agent.md` 重复的大段角色细化
- 以“逐 change-id 的 records 目录迭代日志”为主口径的旧表述
- 含糊不清的“按落地方案 §6.1”但未指明来源的写法

### 补充

- 明确一句：`agent_team_project` 是默认运行时后端，不是治理规则权威源
- 明确一句：默认 backend 只支持 5 个执行角色，不覆盖文档 Agent、Bug 修复 Agent
- 明确一句：主 Agent 默认不直接执行具体技能，仅统筹、决策、审核、闭环
- 给出清晰优先级：`OpenSpec > global-rules > agents > skills > cursor rules > runtime backend`

### 改造建议

将该文件重写为 4 段结构：

1. 身份入口
2. 优先级
3. 默认运行后端说明
4. 行为边界

---

## 4.2 `.cursor/rules/global-rules.mdc`

### 目标

保留为“全局加载入口”，不变成第二份制度文件。

### 保留

- 首次对话时先读取 `projects-rules-for-agent.md` 和 `skills-rules-for-agent.md`
- 先确定执行方和技能，再执行

### 删除

- 无需新增复杂制度

### 补充

- 增加一句：角色与技能的权威来源分别是 `agents/*.md` 与 `skills-rules-for-agent.md`
- 增加一句：若当前选择 `agent_team_project` 作为运行后端，则其只负责执行，不覆盖规则层

---

## 4.3 `OpenSpec.md`

### 目标

回到唯一“项目宪法”定位，消除日志双轨。

### 保留

- 文档定位与 AI 协作关系
- `design/documents/[change-id] -> openspec/changes/[change-id]` 的变更启动顺序
- `project-early-phase` 机制
- `proposal/tasks/design/spec` 的目录与职责说明

### 删除或改写

- 所有把“逐 change-id 的 records 目录迭代日志”写成主日志方案的段落
- 第 5.1、6.2、6.3 中与第 1.1 项目级单一日志冲突的表述

### 补充

- 在 1.1 明确声明：项目级统一日志是唯一主口径
- 在 5.1、6.2、6.3 中全部改为引用项目级日志
- 增加一句：`records/` 仅用于收纳变更级记录类文档，不再承担主日志职责

### 优先改造段

- 1.1 `design/documents/` 定位
- 5.1 `project-early-phase`
- 6.2 变更启动检查清单
- 6.3 新项目 0-1 说明

---

## 4.4 `global-rules/projects-rules-for-agent.md`

### 目标

成为唯一“项目执行与收尾规则”来源。

### 保留

- 任务执行通用机制
- 执行前自检
- 变更入口
- 任务推进
- 安全/配额/行为约束

### 删除或改写

- “主 Agent 自己执行时”这类会导致边界模糊的表述，除非后续明确降级映射机制
- 与单一日志口径冲突的旧表述

### 补充

- 明确：主 Agent 默认不直接执行技能
- 明确：若未来允许主 Agent 降级执行，须显式映射为某子 Agent 角色执行，而非以主 Agent 直接执行
- 明确：`agent_team_project` 属于运行时后端，执行后仍要满足本规则的日志与闭环要求

### 建议处理方式

优先采用方案 A：

- 主 Agent 不直接执行技能
- 执行方始终是某子 Agent 或运行后端中的执行角色

---

## 4.5 `global-rules/skills-rules-for-agent.md`

### 目标

成为唯一“Agent 与 Skill 对应关系”来源。

### 保留

- 主 Agent/产品/架构/前端/后端/测试/文档/Bug 修复的技能关系表
- 各技能触发场景与职责

### 删除或改写

- 与项目级单一日志冲突的“逐 change-id 的 records 目录迭代日志”主日志写法
- 容易让人理解成“所有执行必须通过 skills/ 目录直接落地”的绝对化表述

### 补充

- 明确区分：
  - 治理层技能映射
  - 运行时后端执行实现
- 增加一句：当选择 `agent_team_project` 作为默认 backend 时，其可不逐次加载 `skills/*/SKILL.md`，但其执行结果仍受技能治理要求和审核要求约束

### 说明

这一步是为了让“2.0 原方案运行时”与“后续严格 SKILL 路径”能够共存，而不是互相否定。

---

## 4.6 `agents/主Agent.md`

### 目标

保留为主 Agent 总纲说明书，但删除运行实现细节。

### 保留

- 主 Agent 的定位：统筹、决策、审核、协同、闭环
- 产出物质量审核与改进表
- 与配额策略相关的治理性表述

### 删除或改写

- 与 `.cursor/rules/agent.mdc` 重复的入口性描述
- 与 `agent_team_project` 具体实现耦合过深的描述
- 与项目级单一日志冲突的旧路径表述

### 补充

- 增加“运行后端”一节：
  - 默认后端：`agent_team_project`
  - 主 Agent 负责选择后端，不负责实现后端
- 增加“角色范围”一节：
  - 说明文档 Agent、Bug 修复 Agent 属于治理角色，但不进入默认 2.0 backend 的 executor
- 明确主 Agent 不直接执行具体技能

---

## 4.7 `agents/README.md`

### 目标

把该文档升级为“角色治理层说明”，不再只讨论 Subagent 对比。

### 保留

- `agents/` 是角色规范权威源
- Subagent 只应作为执行入口，不应重复维护完整角色说明

### 删除或改写

- 容易让人误读为“当前推荐只通过 Subagent 执行”的表述

### 补充

- 增加“与运行后端的关系”章节：
  - `agent_team_project` 是运行后端之一
  - Subagent 是另一类执行载体
  - 两者都受 `agents + global-rules + OpenSpec` 约束
- 明确治理层角色全集由主 Agent 与产品经理、架构、前端、后端、测试、文档、Bug 修复等子 Agent 构成
- 明确“2.0 默认 backend 只覆盖 5 个执行角色”是运行层范围，不与治理层角色全集冲突

---

## 4.8 `agents/子Agent-产品经理.md`

### 保留

- 角色定位
- 技能对应
- 配额与模型边界

### 删除或改写

- 若文中有“默认必须由当前会话直接执行”的暗示，应改成治理表述

### 补充

- 增加一句：在默认 `agent_team_project` backend 中，该角色可作为 5 个执行角色之一被运行时调度

---

## 4.9 `agents/子Agent-架构.md`

### 保留

- 工程结构分析、代码评审、OpenSpec CLI 的职责

### 补充

- 增加一句：在默认 `agent_team_project` backend 中，该角色可作为 5 个执行角色之一被运行时调度

---

## 4.10 `agents/子Agent-前端.md`

### 保留

- coding-implement（前端）主导
- image-analysis 联动
- 前端模型边界

### 补充

- 增加一句：在默认 `agent_team_project` backend 中，该角色可作为 5 个执行角色之一被运行时调度

---

## 4.11 `agents/子Agent-后端.md`

### 保留

- coding-implement（后端）主导

### 补充

- 增加一句：在默认 `agent_team_project` backend 中，该角色可作为 5 个执行角色之一被运行时调度

---

## 4.12 `agents/子Agent-测试.md`

### 保留

- func-test 主导
- 两轮 `openspec validate` 要求
- 慢速/轻量模型边界

### 补充

- 增加一句：在默认 `agent_team_project` backend 中，该角色可作为 5 个执行角色之一被运行时调度

---

## 4.13 `agents/子Agent-文档.md`

### 目标

保留为治理角色，不进入默认 backend executor。

### 保留

- 规范文档维护职责
- 与主 Agent/架构的审核关系

### 补充

- 明确一句：默认 `agent_team_project` backend 不直接调度文档 Agent；该角色由主 Agent 在治理层按需调用

---

## 4.14 `agents/子Agent-Bug修复.md`

### 目标

保留为治理角色，不进入默认 backend executor。

### 保留

- 根因分析、最小改动修复、回归联动

### 补充

- 明确一句：默认 `agent_team_project` backend 不直接调度 Bug 修复 Agent；该角色由主 Agent 在治理层按需调用

---

## 4.15 `agent_team_project/README.md`（需新增）

### 目标

为运行后端正名，避免继续被误读为总规范。

### 必须新增内容

- 定位：2.0 近全自动闭环运行时后端
- 主链路：
  - `write_decision`
  - `cursor_decision.json`
  - `run_skill.py`
  - `dynamic_agent_skill.py`
  - `cursor_feedback.txt`
  - 插件复制剪贴板
  - Chat 再决策
- backend scope：
  - 仅 5 个 executor
  - 非治理规则权威源
- 与治理层关系：
  - 受 `OpenSpec/global-rules/agents` 约束
  - 不定义最终日志制度
  - 不定义最终角色全集
  - 不定义最终配额权威
- 运行配置说明：
  - `runtime_config.json` 是运行层单一配置源
  - README 须解释其字段结构与默认模型调用策略
  - README 须明确“Cursor Auto 优先 / API fallback”的当前实现边界

---

## 4.16 `agent_team_project/dynamic_agent_skill.py`

### 目标

保留其 2.0 原方案核心作用，但去硬编码、去双头定义。

### 保留

- LangGraph 状态流转
- 执行 -> 收集反馈 -> 写 `cursor_feedback.txt`
- `agent_state.json`
- `task_*.txt`

### 删除或改写

- 硬编码模型名 `gpt-4-turbo` / `gpt-3.5-turbo`
- 代码注释中带有“复杂任务用GPT-4，简单任务用GPT-3.5，降低成本”这类已经与治理层冲突的模型策略
- 容易让人误解其为“完整角色规范实现”的提示词措辞

### 补充

- 从配置文件加载：
  - executor 列表
  - 模型调用策略
  - fallback 模型候选顺序
  - timeout
  - base_url
- 在文件头部新增注释：
  - 这是 runtime backend，不是治理规则定义文件
- 明确 `executor_agents` 仅对应默认 backend 的 5 个执行角色
- 可选：输出中增加 `backend_name=inline-langgraph`
- 优先尝试 `cursor_builtin` provider，失败后自动降级到 `api` provider
- 当前若未接入 Cursor 内置模型桥接器，需在日志中清晰说明是“按策略降级”而非静默失败

### 可选增强

- 把 `task_results` 的 key 统一为字符串或整数，避免恢复历史状态时类型不一致
- 避免按 `task_list[int(k)-1]` 推测 executor 文件名，改为显式保存 task meta

---

## 4.17 `agent_team_project/agent_team_mcp_server.py`

### 目标

保留为 `write_decision` 主方案实现，但去重复角色定义。

### 保留

- `write_decision` schema 校验
- `cursor_decision.json` 写入
- `VALIDATION_ERROR` / `WRITE_ERROR`

### 删除或改写

- 在代码中直接重复维护 executor 枚举

### 补充

- 从统一配置源读取 executor 列表
- 在注释中写明：该枚举是“默认 runtime backend 支持的执行角色集合”，不是治理层全角色集合

---

## 4.18 `agent_team_project/run_skill.py`

### 目标

保留为触发器，但增强稳健性。

### 保留

- 读取 `cursor_decision.json`
- 调用 `dynamic_agent_skill.py`
- 处理反馈文件

### 删除或改写

- `shell=True` 拼接命令的实现方式

### 补充

- 改成参数数组调用，避免 JSON 转义脆弱问题
- 注释明确：它只负责触发 runtime backend，不负责治理决策

---

## 4.19 `agent_team_project/runtime_config.json`（需新增）

### 目标

承接运行层配置，消除模型和角色重复硬编码。

### 建议字段

```json
{
  "backend_name": "inline-langgraph",
  "executors": ["产品经理", "架构师", "前端工程师", "后端工程师", "测试工程师"],
  "model_strategy": {
    "preferred_provider": "cursor_builtin",
    "fallback_provider": "api",
    "cursor_builtin": {
      "enabled": true,
      "mode": "Auto"
    },
    "api": {
      "enabled": true,
      "models": {
        "simple": ["Qwen/Qwen3-8B", "Qwen/Qwen3.5-4B"],
        "complex": ["Pro/deepseek-ai/DeepSeek-V3.2", "Pro/MiniMaxAI/MiniMax-M2.5"]
      }
    }
  },
  "llm": {
    "temperature": 0.1,
    "timeout_seconds": 60
  },
  "run_skill": {
    "timeout_seconds": 300
  }
}
```

### 当前落地说明

- 已将 executor 与模型调用策略统一收敛到 `runtime_config.json`
- 当前优先策略为 `Cursor Auto`
- 当前 fallback 为 API 模型链路
- 当前仓库尚未接入 Cursor 内置模型桥接器，因此现状是“先尝试 Cursor provider，再自动降级到 API provider”

---

## 4.20 `architecture/agent-governance-and-runtime.md`（需新增）

### 目标

作为 V2.1 核心总纲文档，避免以后再次散落到多个规则文件里。

### 必须包含

- 三层架构
- 权威优先级
- 默认 backend
- 角色全集 vs backend executor 子集
- 日志口径
- 模型策略分层

---

## 4.21 外部方案文档联动

目标目录：

- `otherDocuments/【方案】Cursor 多Agent协同2.0(真协同)/`

### 需要补充的说明

建议在原 2.0 方案文档后续新增一个“V2.1 补充说明”章节，说明：

- 2.0 文档描述的是默认运行时后端
- V2.1 新增了治理层与运行层分离
- `agent_team_project` 依然有效，但不再承担总规范职责

## 5. 执行顺序建议

### 第一阶段：先收敛文档权威

1. 改 `OpenSpec.md`
2. 改 `projects-rules-for-agent.md`
3. 改 `skills-rules-for-agent.md`
4. 改 `agents/主Agent.md`
5. 改 `.cursor/rules/agent.mdc`

### 第二阶段：再给 runtime backend 正名

1. 新增 `agent_team_project/README.md`
2. 新增 `runtime_config.json`
3. 改 `dynamic_agent_skill.py`
4. 改 `agent_team_mcp_server.py`
5. 改 `run_skill.py`

### 第三阶段：最后补统一总纲

1. 新增 `architecture/agent-governance-and-runtime.md`
2. 回写外部方案目录的 V2.1 文档

## 6. 验收标准

完成 V2.1 改造后，应满足以下标准：

1. 任一规则只在一处定义“谁是权威”。
2. 主 Agent 是否直接执行技能，有唯一答案。
3. 迭代日志路径全仓一致。
4. `agent_team_project` 被明确定义为 runtime backend，而非治理规范源。
5. 模型策略不再同时出现在治理文档和 Python 硬编码中。
6. 角色全集与默认 backend executor 子集之间关系明确，无歧义。

## 7. 最终建议

V2.1 的核心不是“推翻 2.0”，而是：

- 保住 2.0 的高效近全自动闭环；
- 用 OpenSpec 治理层兜住角色、日志、审核、配额；
- 把 `.cursor/rules/agent.mdc` 从“超级制度汇编”降回“总指挥入口”；
- 把 `agent_team_project` 从“看起来像总规范”归位为“默认运行后端”。

这样后续无论接入 Cursor Subagent、更多 MCP 工具，还是新增 `skills-subagent` backend，都不会再造成规则多头定义。
