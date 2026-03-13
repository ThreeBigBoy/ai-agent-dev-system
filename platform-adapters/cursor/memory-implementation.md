## Cursor 宿主下的 memory 沉淀集成说明（V2.3 / V2.3.1）

> 目标：在 Cursor 中，为 `ai-agent-dev-system` 提供一条尽可能自动化、但仍安全可控的长期记忆（memory/）沉淀路径。

### 1. 触发主体与判定规则

- **触发主体**：主 Agent，根据 `OpenSpec + global-rules + agents/主Agent.md` 中的规则，在复盘 `design/documents/[change-id]/records/` 时判断是否需要沉淀长期记忆。
- **判定原则（简要）**：
  - 某类经验或坑点在 ≥2 个不同 `change-id` 的 records/ 中反复出现；
  - 本次复盘明确给出了可复用的模式 / SOP / 反模式 / 偏好等抽象经验；
  - 用户在对话中显式表达「希望写入长期记忆」；
  - preference 类型的记忆在写入前必须获得用户确认。

详细规则应以方案文档第三部分与 `agents/主Agent.md` 中的「长期记忆沉淀」小节为准。

### 2. 脚本接口（统一，支持自动正文）

在 Cursor 中，建议直接调用以下脚本创建 memory 条目（从仓库根目录运行）。脚本已在 V2.3.1 中扩展，支持通过 `--body-file` 或 stdin 传入完整正文。

```bash
# 方式一：仅生成骨架（不传正文，后续人工/Agent 补写）
python3 scripts/memory/create_memory_entry.py \
  --type pattern \
  --title "<记忆标题>" \
  --change-id <source-change-id> \
  --tags tag1,tag2 \
  --applicable-projects ai-agent-dev-system \
  --host-scope cursor

# 方式二：通过 stdin 传入完整正文（推荐用于自动化闭环）
python3 scripts/memory/create_memory_entry.py \
  --type pattern \
  --title "<记忆标题>" \
  --change-id <source-change-id> \
  --tags tag1,tag2 \
  --applicable-projects ai-agent-dev-system \
  --host-scope cursor,vscode << 'EOF'
# <记忆标题>

## 背景与适用场景
...

## 推荐做法（步骤 / Checklist）
...

## 反例与常见误区（如有）
...

## 与现有规范/技能的关系
...
EOF

# 方式三：通过 --body-file 传入正文文件
python3 scripts/memory/create_memory_entry.py \
  --type pattern \
  --title "<记忆标题>" \
  --change-id <source-change-id> \
  --tags tag1,tag2 \
  --applicable-projects ai-agent-dev-system \
  --host-scope cursor \
  --body-file /tmp/memory-body.md
```

- `--type`：pattern / anti-pattern / preference / playbook / reflection；
- `--change-id`：来源变更 ID（例如 `sys-infra-memory-v1`）；
- `--tags`：用于后续检索的标签（如 openspec,change-flow,runtime-logs 等）；
- `--applicable-projects`：通常为 `ai-agent-dev-system`，也可使用 `all`；
-- `--host-scope`：Cursor 优先可填写 `cursor`，如需复用到其他宿主可扩展为 `cursor,vscode,continue`。  
脚本会在 `memory/*/` 下生成一个带 frontmatter 的 Markdown 文件：  
- 当提供 `--body-file` 或通过 stdin 传入非空正文时，正文即为传入内容；  
- 当未提供 `--body-file` 且 stdin 为空时，仅生成带小节骨架的空白正文，并在 stdout 显式提示「只生成骨架，需后续手动补充内容」。

### 3. 建议的自动化程度（含自动正文写入）

- **当前阶段（半自动，推荐闭环）**：
  - 主 Agent 在复盘结束且判定需要沉淀记忆时：
    - 在 Chat 中先根据本次 `change-id` 与 records 摘要，生成一段符合记忆类型的 Markdown 正文草稿（仅包含 `# 标题` 与各小节，不含 frontmatter）；
    - 给出使用 stdin 或 `--body-file` 的命令示例（如上「方式二/方式三」），并将正文一并展示，方便用户复制到 Terminal 或临时文件中执行；
    - 由用户在 Cursor Terminal 中执行该命令；
    - 主 Agent 随后在对应的 `design/documents/[change-id]/records/` 文档末尾追加一句引用新建 memory 条目的记录。

- **未来增强（可选，自动执行）**：
  - 在用户默认信任前提下，由主 Agent 直接通过 Shell 工具调用脚本，将生成的正文通过 HEREDOC 形式传入 stdin，实现全自动落盘；
  - 或通过 Cursor 自定义扩展，将该脚本挂在一个命令面板命令上，由主 Agent 在对话中提示用户触发，并将当前会话中生成的正文作为 body 注入。

### 4. 与 runtime-logs 的关系

- runtime-logs 记录的是**技术指标与运行事件**，由 `scripts/runtime-logging/append_cursor_model_call.py` 写入；
- memory 记录的是**跨 change-id 的长期经验**，由本文件描述的 `create_memory_entry.py` 写入；
- 二者都在 Cursor 宿主下由主 Agent 根据规则触发，但作用层次不同、文件目录不同。

