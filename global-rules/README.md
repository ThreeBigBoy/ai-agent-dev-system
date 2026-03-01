# global-rules 说明与规则来源配置

本目录（`ai-agent-dev-system/global-rules/`）下为全局规则 Markdown 文件，供多项目复用。  
**仅把文件放在此目录并不会让 Cursor 自动加载为规则**，需在 Cursor 中显式配置为规则来源后才会生效。

---

## 检查结论：是否已配置为规则来源？

- **项目内（仓库内）**：ai-agent-dev-system 下无 `.cursor/rules/`，Proj01ShopifyTheme 仅有根目录 `.cursorrules`，**仓库内未**将 `global-rules/*.md` 配置为规则来源。
- **用户级**：若你已在 **Cursor 用户级 Rules** 中增加「读取并遵循 `ai-agent-dev-system/global-rules/` 下对应 md 文件」的规则，则 **`global-rules` 已作为规则来源之一生效**。用户级 Rules 存于 Cursor 应用配置中，本仓库无法直接读取，需你在 Cursor Settings → Rules for AI 中自行确认该条已保存且路径正确。

**需遵循的规则文件**（本目录下除 README 外的 .md，供你与用户级规则表述核对）：

| 文件 | 用途 |
|------|------|
| `projects-rules-for-agent.md` | 项目通用规则：代码/安全/配额/行为、OpenSpec 变更入口等 |
| `skills-rules-for-agent.md` | 技能与 Agent 对应、先读 SKILL 再执行等 |
| `readme-rules-for-agent.md` | README 编写与维护规范 |

---

## 如何将 global-rules 配置为规则来源（二选一或兼用）

### 方式一：多根工作区 + 第一个根目录的 .cursor/rules（推荐）

1. 用 Cursor 打开**多根工作区**，且把 **ai-agent-dev-system** 包含进来（并尽量作为第一个根目录，因 Cursor 多根时仅从“第一个”项目加载 `.cursor/rules/`）。
2. 在 **ai-agent-dev-system** 下创建 **`.cursor/rules/`**，并在其中添加 `.mdc` 规则文件，在规则**内容**中引用或摘录本目录下的规范，例如：
   - 创建 `ai-agent-dev-system/.cursor/rules/global-rules.mdc`，frontmatter 设 `alwaysApply: true`，正文里用「请始终遵循以下规范」并粘贴或引用 `projects-rules-for-agent.md`、`skills-rules-for-agent.md` 等关键内容；或
   - 在 `.mdc` 中写：打开对话时先读取 `ai-agent-dev-system/global-rules/projects-rules-for-agent.md` 与 `skills-rules-for-agent.md`，再按其中约定执行。
3. 保存后，在包含 ai-agent-dev-system 的多根工作区中，Cursor 会从该第一个项目的 `.cursor/rules/` 加载规则，从而间接使 `global-rules` 的约定生效。

### 方式二：用户级 / 全局 Rules

1. 打开 Cursor → **Settings** → **Rules for AI**（或 **Cursor Settings → General → Rules**，以实际界面为准）。
2. 在**用户级 / 全局规则**中增加一条，内容示例：
   - 「当在本工作区或 ai-agent-dev-system 相关项目中时，须先读取并遵循 `ai-agent-dev-system/global-rules/projects-rules-for-agent.md` 与 `ai-agent-dev-system/global-rules/skills-rules-for-agent.md`；若工作区中包含 ai-agent-dev-system，则打开对话时优先加载上述两文件作为规则。」
3. 保存后，只要 Cursor 能访问到 ai-agent-dev-system 路径（例如多根工作区中包含该文件夹），全局规则即会引用 `global-rules` 下的内容。

---

## 验证是否生效

- 在对话中发起与新需求/新建变更相关的请求（如「帮我做 XXX 功能」），看 AI 是否**先**提及或执行「读取 OpenSpec 第六节与 4.3 节」「先 design/documents 再 openspec/changes」等来自 `projects-rules-for-agent.md` 的约定；若会，则说明 `global-rules` 已被作为规则来源之一生效。
- 若不会，则需按上节任一方式补配规则来源，或确认 ai-agent-dev-system 是否在 Cursor 当前工作区内且路径正确。
