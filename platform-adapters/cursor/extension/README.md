## Cursor 扩展与插件说明（extension）

本目录用于存放与 Cursor 自定义扩展相关的**说明与示例**，例如：

- 监听运行后端反馈文件并复制到剪贴板的插件；  
- 通过快捷键触发 `runtime_trigger` 的命令；  
- 其他用于改进多 Agent 运行体验的 Cursor 扩展。

> 这里仅存放文档与示例，不包含必须安装的二进制或第三方代码。  
> 具体扩展实现可以按个人偏好存放在其他仓库，并在此处链接说明。

### 1. 实际插件代码推荐放置位置（Cursor 宿主）

- **推荐实践（与 V2.2 运行后端配套）**
  - 当你以 `ai-agent-dev-system` 为工作区根，且运行后端目录为 `agent_team_project/` 时，建议将实际可执行的 Cursor 插件代码放在：
    - `agent_team_project/.vscode/extensions/cursor-agent-extension/`
    - 其中通常包含：
      - `extension.js`：插件核心逻辑（例如监听 `agent_feedback.txt` 并复制到剪贴板）
      - `package.json`：插件配置

- **说明**
  - `platform-adapters/cursor/extension/` 作为 **adapter 文档层**，只负责说明「Cursor 应该如何接线扩展」和给出示例结构；  
  - Cursor 真正加载的扩展代码，可以：
    - 放在当前仓库的 `agent_team_project/.vscode/extensions/` 下，由工作区级扩展机制加载（本仓库当前使用的方式）；  
    - 或按个人习惯安装到 Cursor 支持的全局/用户扩展目录，但此时需自行确保能访问运行后端所在工作区。

### 2. 与早期方案文档的对应关系

- 早期 V2.0/V2.1 方案中的推荐结构示例为：

```plaintext
agent_team_project/
├── .env
├── dynamic_agent_skill.py
├── run_skill.py
├── agent_decision.json / cursor_decision.json
├── agent_feedback.txt  / cursor_feedback.txt
└── .vscode/
    └── extensions/
        └── cursor-agent-extension/
            ├── extension.js
            └── package.json
```

- 在 V2.2 下，该结构仍然有效，含义调整为：
  - **运行后端根目录**：`agent_team_project/`
  - **工作区级插件代码实际所在位置**：`agent_team_project/.vscode/extensions/cursor-agent-extension/`
  - **本目录（platform-adapters/cursor/extension）**：只负责存放扩展相关的文档、示例与约定，不承担插件实际安装/加载职责。
