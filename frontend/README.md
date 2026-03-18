# 前端组件（HC 人工确认）

本目录存放与 LangGraph 后端配合的前端组件，当前包含：

- **ConfirmPanel** (`src/components/ConfirmPanel.tsx`)：人工确认弹窗，支持 approve / reject / comment，与 MCP `human_confirm_submit` 及后端 `POST /confirm/submit` 对齐。

## 使用方式

1. 在已有 React 项目中安装依赖后，将 `src/components/ConfirmPanel.tsx` 与 `ConfirmPanel.css` 拷贝到项目中，或通过 monorepo 引用。
2. 当后端返回 `status: "waiting_hc2"` 或 `waiting_hc7` 时，可调用 `GET /confirm/pending?change_id=xxx` 或 MCP 工具 `human_confirm_poll` 获取待确认项，渲染 `<ConfirmPanel ... onClose={...} onSubmit={...} />`。
3. `onSubmit` 中调用 `POST /confirm/submit` 或 MCP `human_confirm_submit`，并落盘对应 step4.5/step7.5 确认记录文件，再调用 `run_langgraph` 继续执行。

## 技术栈

- React 18+
- TypeScript（可选，组件为 .tsx）
