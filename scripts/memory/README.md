## `scripts/memory/`：长期记忆辅助脚本

本目录存放与根级 `memory/` 长期记忆库协作的辅助脚本。

### `create_memory_entry.py`

创建新的长期记忆条目文件，并生成符合 `memory/schema.md` 规范的 frontmatter 与最小正文骨架。

#### 使用示例（从仓库根目录运行）

```bash
python3 scripts/memory/create_memory_entry.py \
  --type pattern \
  --title "OpenSpec 变更标准流程（最小实践）" \
  --change-id sys-infra-memory-v1 \
  --tags openspec,change-flow \
  --applicable-projects ai-agent-dev-system \
  --host-scope cursor,vscode
```

脚本会：

- 根据 `--type` 决定放入 `memory/patterns/`、`memory/anti-patterns/`、`memory/preferences/`、`memory/playbooks/` 或 `memory/reflections/`；
- 为 `id` 自动生成一个带时间戳的标识（或使用 `--id` 覆盖）；
- 生成包含以下字段的 frontmatter：
  - `id` / `title` / `type` / `tags`；
  - `applicable_projects` / `host_scope`；
  - `source_change_ids`（包含传入的 `--change-id`）；
  - `created_at` / `last_reviewed_at` / `maturity`；
  - 可选 `owner`；
- 根据类型写入最小正文骨架（pattern / anti-pattern / preference / playbook / reflection 各有不同结构）。

> 建议：在主 Agent 判定需要沉淀长期记忆时，由宿主适配层调用本脚本，并在对应的 `design/documents/[change-id]/records/` 文档中追加对新建 memory 条目的引用。

