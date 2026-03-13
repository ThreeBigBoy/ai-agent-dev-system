## Cursor 宿主下的 memory 沉淀集成说明（V2.3）

> 目标：在 Cursor 中，为 `ai-agent-dev-system` 提供一条尽可能自动化、但仍安全可控的长期记忆（memory/）沉淀路径。

### 1. 触发主体与判定规则

- **触发主体**：主 Agent，根据 `OpenSpec + global-rules + agents/主Agent.md` 中的规则，在复盘 `design/documents/[change-id]/records/` 时判断是否需要沉淀长期记忆。
- **判定原则（简要）**：
  - 某类经验或坑点在 ≥2 个不同 `change-id` 的 records/ 中反复出现；
  - 本次复盘明确给出了可复用的模式 / SOP / 反模式 / 偏好等抽象经验；
  - 用户在对话中显式表达「希望写入长期记忆」；
  - preference 类型的记忆在写入前必须获得用户确认。

详细规则应以方案文档第三部分与 `agents/主Agent.md` 中的「长期记忆沉淀」小节为准。

### 2. 脚本接口（统一）

在 Cursor 中，建议直接调用以下脚本创建 memory 条目（从仓库根目录运行）：

```bash
python3 scripts/memory/create_memory_entry.py \
  --type pattern \
  --title "<记忆标题>" \
  --change-id <source-change-id> \
  --tags tag1,tag2 \
  --applicable-projects ai-agent-dev-system \
  --host-scope cursor
```

- `--type`：pattern / anti-pattern / preference / playbook / reflection；
- `--change-id`：来源变更 ID（例如 `sys-infra-memory-v1`）；
- `--tags`：用于后续检索的标签（如 openspec,change-flow,runtime-logs 等）；
- `--applicable-projects`：通常为 `ai-agent-dev-system`，也可使用 `all`；
- `--host-scope`：Cursor 优先可填写 `cursor`，如需复用到其他宿主可扩展为 `cursor,vscode,continue`。

脚本会在 `memory/*/` 下生成一个带 frontmatter 的 Markdown 文件，并根据类型写入最小正文骨架。

### 3. 建议的自动化程度

- **当前阶段（半自动）**：
  - 主 Agent 在复盘结束且判定需要沉淀记忆时：
    - 在对话中给出上述命令示例（填好 type/title/change-id/tags 等）；
    - 由用户在 Cursor Terminal 中执行该命令；
    - 主 Agent 随后在对应的 `design/documents/[change-id]/records/` 文档末尾追加一句引用新建 memory 条目的记录。

- **未来增强（可选）**：
  - 在用户默认信任前提下，由主 Agent 直接通过 Shell 工具调用脚本，无需用户手动运行；
  - 或通过 Cursor 自定义扩展，将该脚本挂在一个命令面板命令上，由主 Agent 在对话中提示用户触发。

### 4. 与 runtime-logs 的关系

- runtime-logs 记录的是**技术指标与运行事件**，由 `scripts/runtime-logging/append_cursor_model_call.py` 写入；
- memory 记录的是**跨 change-id 的长期经验**，由本文件描述的 `create_memory_entry.py` 写入；
- 二者都在 Cursor 宿主下由主 Agent 根据规则触发，但作用层次不同、文件目录不同。

