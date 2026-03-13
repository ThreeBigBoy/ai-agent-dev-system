## `sys-infra-memory-v1` 任务清单

> 参考方案文档：`otherDocuments/【方案】Cursor 多Agent协同2.0(真协同)/V2.3/runtime-logging-and-agent-memory-integrated.md`

- [x] 1.1 创建 `runtime-logs/` 目录结构
  - [x] 创建 `runtime-logs/` 根目录与 `.gitignore`，忽略 `.jsonl` / `.log` 等运行期产物
  - [x] 创建 `runtime-logs/model-calls/` 与 `runtime-logs/system-events/` 子目录
  - [x] 创建 `runtime-logs/adapters/` 目录及各宿主占位文档（如 `cursor.md`、`vscode.md`、`continue.md`、`openai-codex.md`、`generic.md`）
  - [x] 编写 `runtime-logs/README.md`，说明运行日志定位、目录结构与数据字段

- [x] 1.2 创建 `memory/` 目录结构
  - [x] 创建 `memory/` 根目录与子目录：`patterns/`、`anti-patterns`、`preferences`、`playbooks`、`reflections`
  - [x] 编写 `memory/README.md`，说明长期记忆定位、分类与使用方式
  - [x] 编写 `memory/schema.md`，定义 frontmatter 规范与示例

- [x] 1.3 创建示例记忆条目（验证规范）
  - [x] 在 `patterns/` 下创建 `openspec-change-workflow.md` 示例（变更标准流程）
  - [x] 在 `anti-patterns/` 下创建 `example-pitfall.md` 示例（常见陷阱）
  - [x] 在 `preferences/` 下创建 `user-coding-style.md` 示例（用户编码风格偏好）

- [x] 1.4 与现有规则联动校验
  - [x] 检查 `global-rules/projects-rules-for-agent.md` 中与运行日志和长期记忆相关的条款是否与本变更保持一致
  - [x] 在 `design/documents/sys-infra-memory-v1/` 中补充本次变更的实施记录与后续优化建议（records/）

- [x] 2.1 Cursor 宿主适配与采集试点（方案第二阶段）
  - [x] 在 `platform-adapters/cursor/` 下编写 `runtime-logging-implementation.md`，说明如何在 Cursor 中将模型调用与系统事件写入 `runtime-logs/`
  - [x] 在 `runtime-logs/README.md` 中补充与 Cursor 适配示例一致的日志示例行

- [x] 2.2 VS Code 宿主适配占位（方案第二阶段）
  - [x] 在 `platform-adapters/vscode/` 下编写 `runtime-logging-implementation.md`，说明在 VS Code 中推荐的写入 `runtime-logs/` 的最小方案

- [x] 3.1 将运行日志与长期记忆嵌入主 Agent 闭环流程（方案第三阶段）
  - [x] 在 `agents/主Agent.md` 中补充「运行日志与长期记忆（V2.3 扩展）」小节，约定：
    - 何时触发 `runtime-logs/model-calls` 与 `runtime-logs/system-events` 的记录
    - 何时触发根级 `memory/` 下的长期记忆沉淀

- [x] 3.2 在核心 SKILL 中嵌入长期记忆检索（方案第三阶段）
  - [x] 在 `skills/request-analysis/SKILL.md` 的整体流程中增加第 0 步，说明如何在根级 `memory/` 中检索与需求分析相关的长期记忆
  - [x] 在 `skills/project-analysis/SKILL.md` 的总体工作流程中增加第 0 步，说明如何在根级 `memory/` 中检索与工程结构相关的长期记忆

