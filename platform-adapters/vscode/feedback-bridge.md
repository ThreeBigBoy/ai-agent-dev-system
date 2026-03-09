## VS Code Feedback Bridge

本文件用于规划 ai-agent-dev-system 在 VS Code 宿主下的 **反馈桥接（feedback_bridge）** 实现方式。

### 1. 抽象目标

与 Cursor adapter 一样，VS Code 下的 feedback bridge 也只需满足一个抽象目标：

- **运行后端产生的执行结果，应能够回到主 Agent 或对应子 Agent 的对话上下文中**，以便继续决策或宣告闭环。

### 2. 可能的实现方式（示例）

具体实现取决于 VS Code 当下提供的 API 能力，这里列出若干可选思路：

1. **通过 VS Code Agent API 直接发送消息**  
   - 若 VS Code 提供从扩展向 Agent 对话注入消息的 API，可在运行后端完成后直接调用该 API，附上执行结果。  
   - 这是理想方案，可实现全自动桥接。

2. **通过输出面板 + 快捷插入**  
   - 运行后端将反馈写入某个日志文件或终端输出；  
   - VS Code 扩展将该内容显示在输出面板，并提供「插入到当前 Agent Chat」的快捷按钮。  

3. **通过剪贴板 + 提示**  
   - 若暂不具备直接写入 Chat 的能力，可类似 Cursor adapter：  
     - 扩展监听反馈文件；  
     - 将反馈复制到剪贴板；  
     - 弹窗提示用户在 Agent Chat 中粘贴。

### 3. 协议与文档约定

- 无论采用哪种方式，本机制都只属于 VS Code adapter 的「宿主接线层」，不改变：  
  - OpenSpec；  
  - `global-rules/*.md`；  
  - `agents/*.md`；  
  - `skills/*/SKILL.md`。
- 具体实现与限制可在本文件或子文档中持续补充，但应保持对外抽象为统一的 `feedback_bridge` 能力。

