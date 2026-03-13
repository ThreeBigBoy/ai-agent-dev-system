## `sys-infra-memory-v1` 变更说明（运行日志与长期记忆体系）

本变更用于在 `ai-agent-dev-system` 仓库内落实「运行日志与长期记忆综合设计方案（V2.3）」的第一阶段工作，包含：

- 在仓库根目录下建立 `runtime-logs/` 运行日志目录结构；
- 在 `know-how/` 下建立 `memory/` 长期记忆库及其子目录；
- 为上述两部分编写基础使用说明与 schema 文档；
- 创建若干示例记忆条目，用于验证 frontmatter 规范与检索思路。

设计与实施细节以方案文档 `otherDocuments/【方案】Cursor 多Agent协同2.0(真协同)/V2.3/runtime-logging-and-agent-memory-integrated.md` 为依据。

