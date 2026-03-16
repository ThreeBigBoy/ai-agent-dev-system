# Cursor 从 0 开始初始化配置 SOP 与 GUI 走查清单

## 1. 适用对象

适用于首次从 Git 下载 `ai-agent-dev-system`，希望在 **Cursor IDE** 中直接跑通多 Agent 协同系统的用户。

## 2. 目标结果

完成本手册后，应达到以下状态：

1. Cursor 能自动加载仓库根目录 `.cursor/rules/*.mdc`
2. Chat 默认以主 Agent 身份工作
3. MCP `agent-team` 可写入决策文件
4. 运行后端可读取决策并输出反馈
5. 本地反馈插件可监听反馈文件并复制到剪贴板

## 3. 前置条件

- 已安装 Cursor
- 已安装 Python 3
- 已将本仓库克隆到本机，例如：

```bash
git clone <your-repo-url>
cd ai-agent-dev-system
```

## 4. 初始化配置 SOP

### 4.1 打开正确的工作区

用 Cursor 打开仓库根目录：

- 工作区根目录：`ai-agent-dev-system/`

不要只打开 `agent_team_project/`，否则 `.cursor/rules/` 不会自动生效。

### 4.2 安装 runtime 依赖

在仓库根目录执行：

```bash
pip3 install mcp jsonschema python-dotenv langchain-openai langgraph pydantic
```

若你的环境已安装，可跳过。

### 4.3 配置个人 API 环境变量

在 `agent_team_project/` 下准备 `.env`，至少包含：

```env
OPENAI_API_KEY=your_key
OPENAI_API_BASE_URL=https://api.siliconflow.cn/v1
```

说明：

- Cursor 属于白名单宿主，主 Agent 与子 Agent 默认优先使用宿主内置模型
- 上述 API 主要用于 fallback 或运行后端的 API 链路

### 4.4 配置 MCP

打开：

- `~/.cursor/mcp.json`

参考模板：

- `platform-adapters/cursor/mcp.template.json`

确保 `agent-team` 至少包含：

```json
{
  "command": "python3",
  "args": [
    "/ABS/PATH/TO/ai-agent-dev-system/agent_team_project/agent_team_mcp_server.py"
  ],
  "env": {
    "AGENT_TEAM_PROJECT_ROOT": "/ABS/PATH/TO/ai-agent-dev-system/agent_team_project",
    "AGENT_HOST_TYPE": "cursor"
  }
}
```

配置完成后重启 Cursor。

### 4.5 启用本地反馈插件

本仓库已包含本地插件源码：

- `agent_team_project/.vscode/extensions/cursor-agent-extension/package.json`
- `agent_team_project/.vscode/extensions/cursor-agent-extension/extension.js`

目标行为：

- 监听 `agent_feedback.txt` / `cursor_feedback.txt`
- 检测变化后复制反馈到剪贴板
- 提示你粘贴回 Cursor Chat

若你用本地扩展加载方式，请确保 Cursor 已加载这份扩展。

### 4.6 确认运行时文件命名

当前运行时主命名是：

- `agent_decision.json`
- `agent_feedback.txt`

同时兼容旧名：

- `cursor_decision.json`
- `cursor_feedback.txt`

## 5. 首次运行 SOP

### 5.1 验证规则入口

在 Cursor Chat 中直接问：

```text
你是谁？
```

期望：

- 回答自己是主 Agent / 总指挥

### 5.2 验证 MCP 写入

在 Cursor Chat 中给一个简单需求，让主 Agent 生成并写入决策。

期望出现：

- Chat 中有“决策已写入”的提示
- `agent_team_project/` 下出现：
  - `agent_decision.json`
  - `cursor_decision.json`

### 5.3 验证运行后端

按你的当前触发方式启动 runtime backend。

期望：

- runtime 读取决策
- 生成反馈文件：
  - `agent_feedback.txt`
  - 或兼容旧名 `cursor_feedback.txt`

### 5.4 验证反馈桥

期望：

- 插件弹出“已复制到剪贴板”的提示
- 你能直接粘贴回 Cursor Chat

## 6. 人工 GUI 走查清单

### 6.1 启动阶段

- [ ] Cursor 已打开仓库根目录 `ai-agent-dev-system`
- [ ] 重启后 `.cursor/rules/*.mdc` 已生效
- [ ] Chat 询问身份时回答为主 Agent

### 6.2 MCP 阶段

- [ ] `~/.cursor/mcp.json` 中存在 `agent-team`
- [ ] `AGENT_TEAM_PROJECT_ROOT` 指向 `agent_team_project`
- [ ] `AGENT_HOST_TYPE=cursor`
- [ ] Chat 可正常调用 `write_decision`

### 6.3 runtime 阶段

- [ ] `agent_decision.json` 已生成
- [ ] runtime 可正常执行
- [ ] `agent_feedback.txt` 或 `cursor_feedback.txt` 已生成

### 6.4 反馈闭环阶段

- [ ] 插件已激活
- [ ] 插件能监听反馈文件变化
- [ ] 剪贴板内容可粘贴回 Cursor Chat
- [ ] 主 Agent 能根据反馈继续拆分或结束闭环

## 7. 常见问题

### 7.1 Chat 没有以主 Agent 身份回答

排查：

1. 是否打开的是仓库根目录，而不是 `agent_team_project/`
2. `.cursor/rules/agent.mdc` 是否仍在仓库根目录
3. 是否重启过 Cursor

### 7.2 MCP 不生效

排查：

1. `~/.cursor/mcp.json` JSON 是否合法
2. `python3` 是否可执行
3. `agent_team_mcp_server.py` 路径是否写对
4. 是否补了 `AGENT_HOST_TYPE=cursor`

### 7.3 插件没有复制反馈

排查：

1. 本地扩展是否已激活
2. 当前工作区是否是仓库根目录
3. runtime 是否已经生成 `agent_feedback.txt` 或 `cursor_feedback.txt`
4. 是否有文件权限问题

## 8. 参考文档

- `platform-adapters/cursor/README.md`
- `platform-adapters/cursor/mcp-setup.md`
- `platform-adapters/cursor/runtime-integration.md`
- `platform-adapters/cursor/extension/README.md`
- `platform-adapters/cursor/runtime-logging-implementation.md`
- `platform-adapters/cursor/memory-implementation.md`

> 进阶能力：当你希望对模型调用成本/稳定性进行量化监控，或将多次复盘中提炼出的经验沉淀为长期记忆时，可按上述文档启用 `runtime-logs/` 与根级 `memory/` 能力，并结合 `agents/主Agent.md` 中的运行日志与长期记忆规则使用。

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

