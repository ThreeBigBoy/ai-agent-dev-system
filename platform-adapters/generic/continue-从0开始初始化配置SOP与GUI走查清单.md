# Continue 从 0 开始初始化配置 SOP 与 GUI 走查清单

## 1. 适用对象

适用于首次从 Git 下载 `ai-agent-dev-system`，希望在 **Continue 插件** 中使用多 Agent 协同系统的用户。

## 2. 目标结果

完成本手册后，应达到以下状态：

1. Continue 主会话可读取仓库治理规则
2. 主 Agent 在 Continue 中工作正常
3. 第三方宿主策略生效：主 Agent 用宿主内置模型，子 Agent 走个人 API 模型链路
4. runtime backend 可通过 `AGENT_HOST_TYPE=continue` 正常执行

## 3. 前置条件

- 已安装 Visual Studio Code
- 已安装 Continue 扩展
- 已将本仓库克隆到本机
- 已安装 Python 3

## 4. 初始化配置 SOP

### 4.1 打开仓库根目录

用 VS Code 打开：

- `ai-agent-dev-system/`

### 4.2 安装 runtime 依赖

在仓库根目录执行：

```bash
pip3 install mcp jsonschema python-dotenv langchain-openai langgraph pydantic
```

### 4.3 准备个人 API 环境变量

Continue 属于第三方宿主，子 Agent 默认走个人 API 模型链路，因此这一步是必需的：

```env
OPENAI_API_KEY=your_key
OPENAI_API_BASE_URL=https://api.siliconflow.cn/v1
```

### 4.4 在 Continue 中配置主会话

目标是让 Continue 当前主会话：

1. 读取根 `AGENTS.md`
2. 能访问：
   - `OpenSpec.md`
   - `global-rules/*.md`
   - `agents/*.md`
   - `skills/*/SKILL.md`

建议：

- 将 Continue 当前会话定位为主 Agent 会话
- 把仓库根目录作为可读取上下文

### 4.5 接入 runtime backend

触发 runtime backend 时，显式传入：

```bash
AGENT_HOST_TYPE=continue
AGENT_TEAM_PROJECT_ROOT=/ABS/PATH/TO/ai-agent-dev-system/agent_team_project
```

说明：

- `continue` 会被 runtime 识别为第三方宿主
- 子 Agent 将直接走个人 API 模型候选链路

## 5. 首次运行 SOP

### 5.1 验证主 Agent 入口

在 Continue 会话中问：

```text
你是谁？
```

期望：

- 回答为主 Agent / 总指挥

### 5.2 验证策略分流

让主 Agent 生成一个简单决策并触发 runtime。

期望：

- 主会话仍在 Continue 宿主内运行
- 子 Agent 执行链路直接走 API 模型候选

### 5.3 验证文件链路

期望生成：

- `agent_team_project/agent_decision.json`
- `agent_team_project/agent_feedback.txt`

## 6. 人工 GUI 走查清单

- [ ] Continue 扩展已启用
- [ ] 工作区根目录是 `ai-agent-dev-system`
- [ ] Continue 当前主会话能读取根 `AGENTS.md`
- [ ] 主 Agent 能按治理规则回答
- [ ] 运行时传入了 `AGENT_HOST_TYPE=continue`
- [ ] 运行时传入了 `AGENT_TEAM_PROJECT_ROOT`
- [ ] `agent_decision.json` 已生成
- [ ] `agent_feedback.txt` 已生成

## 7. 常见问题

### 7.1 主会话没按主 Agent 规则工作

排查：

1. Continue 是否拿到了仓库根目录上下文
2. 是否显式要求会话读取根 `AGENTS.md`
3. 是否能访问 `OpenSpec.md` 和 `global-rules/*.md`

### 7.2 runtime 无法执行

排查：

1. 是否安装了 Python 依赖
2. 是否传入 `AGENT_HOST_TYPE=continue`
3. 是否传入 `AGENT_TEAM_PROJECT_ROOT`
4. `.env` 中的 API 凭据是否有效

## 8. 参考文档

- `platform-adapters/generic/continue.md`
- `platform-adapters/generic/README.md`
- `platform-adapters/generic/runtime-logging-implementation.md`
- `scripts/runtime-logging/README.md`
- `scripts/memory/README.md`

> 进阶能力：在 Continue 宿主下，如需记录模型调用成本/状态（runtime-logs）或沉淀跨 change-id 的经验（memory/），可参考上述文档，通过在合适的命令或任务中调用统一脚本接口，向 `runtime-logs/` 与 `memory/` 追加记录。


## 8. 质量保障机制简介（V2.7 新增）

ai-agent-dev-system 采用 **8+1 质量闭环** 确保交付质量。了解这些机制有助于你更好地与 AI 协作：

### 8.1 8+1 质量闭环 v1.3

```
Step 1: 需求分析 → Step 2: PRD 评审 → Step 3: 工程结构分析 → Step 4: 技术方案评审
       → Step 5: 编码实现 → Step 6: 代码评审 → Step 7: 功能验收 → Step 8: 归档 → Step 9: 复盘
```

每个阶段都有**质量门禁检查**，只有 100% 通过才能进入下一阶段。

### 8.2 核心质量保障机制

#### 评审修复循环（Review-Fix Loop）

**关键规则**: **"有条件通过" ≠ "可以进入下一阶段"**

| 评审结论 | 是否可以进入下一阶段 | 后续动作 |
|---------|-------------------|---------|
| **✓ 通过** | ✅ 可以 | 直接进入下一阶段 |
| **△ 有条件通过** | ❌ 不可以 | 必须修复 → 重新评审 → 转为「通过」 |
| **✗ 不通过** | ❌ 不可以 | 必须修复 → 重新评审 → 转为「通过」 |

#### 执行前查阅规范机制

执行任何技能前，主 Agent 会自动完成 4 项查阅：
1. **Skill 版本确认** - 确保使用最新版本 skill
2. **术语定义查阅** - 查阅本阶段关键术语定义
3. **关联 Memory 唤醒** - 唤醒相关的 pattern/anti-pattern
4. **质量门禁检查清单查阅** - 明确准出标准

#### 质量门禁自动化工具

系统提供自动化验证工具：
```bash
# 质量门禁自动化验证
python scripts/openspec-validate/openspec_validate_v2.py --quality-gate
```

### 8.3 关键 Memory 推荐

| Memory | 说明 | 何时阅读 |
|--------|------|---------|
| `pattern-complete-quality-closed-loop` | 8+1 质量闭环完整流程 | 首次了解质量保障机制 |
| `pattern-review-fix-loop` | 评审修复循环模式 | 遇到评审结论为「有条件通过」时 |
| `anti-pattern-terminology-drift` | 术语定义漂移反模式 | 发现沟通理解偏差时 |
| `preference-quality-gate-checklist` | 质量门禁检查清单 | 执行具体阶段任务前 |

> 💡 **提示**: 如果你是新用户，不必一开始就深入阅读所有 Memory。遇到具体场景时，Agent 会自动唤醒相关 Memory。

