const vscode = require('vscode');
const fs = require('fs');
const path = require('path');

function resolveFeedbackFile(workspaceFolder) {
    const candidates = [
        path.join(workspaceFolder, 'agent_feedback.txt'),
        path.join(workspaceFolder, 'cursor_feedback.txt'),
        path.join(workspaceFolder, 'agent_team_project', 'agent_feedback.txt'),
        path.join(workspaceFolder, 'agent_team_project', 'cursor_feedback.txt'),
    ];
    for (const candidate of candidates) {
        if (fs.existsSync(candidate)) {
            return candidate;
        }
    }
    const nestedRuntimeDir = path.join(workspaceFolder, 'agent_team_project');
    if (fs.existsSync(nestedRuntimeDir) && fs.statSync(nestedRuntimeDir).isDirectory()) {
        return path.join(nestedRuntimeDir, 'agent_feedback.txt');
    }
    return path.join(workspaceFolder, 'agent_feedback.txt');
}

function buildMessageForChat(feedbackContent) {
    return `### Agent团队执行反馈\n${feedbackContent}\n请根据反馈判断是否需要调整任务分工，输出新的JSON决策并更新agent_decision.json（兼容旧名 cursor_decision.json）`;
}

function activate(context) {
    const workspaceFolder = vscode.workspace.workspaceFolders?.[0]?.uri?.fsPath;
    if (!workspaceFolder) {
        vscode.window.showErrorMessage("❌ 请先打开 ai-agent-dev-system 工作区，再激活插件！");
        return;
    }
    const feedbackFile = resolveFeedbackFile(workspaceFolder);
    if (!fs.existsSync(feedbackFile)) {
        try {
            fs.mkdirSync(path.dirname(feedbackFile), { recursive: true });
            fs.writeFileSync(feedbackFile, '', 'utf-8');
        } catch (e) {
            vscode.window.showWarningMessage("⚠️ 无法创建反馈文件，请先运行一次 Skill 生成反馈后再依赖插件监听。");
        }
    }
    const watcher = fs.watch(feedbackFile, (eventType) => {
        if (eventType === 'change') {
            setTimeout(() => {
                try {
                    if (!fs.existsSync(feedbackFile)) return;
                    const feedbackContent = fs.readFileSync(feedbackFile, 'utf-8');
                    if (!feedbackContent.trim()) return;
                    const messageForChat = buildMessageForChat(feedbackContent);
                    vscode.env.clipboard.writeText(messageForChat);
                    vscode.window.showInformationMessage("✅ 已读取 Agent 反馈并复制到剪贴板，请在 Cursor Chat 中粘贴并发送！");
                } catch (error) {
                    vscode.window.showErrorMessage(`❌ 读取反馈文件失败：${error.message}`);
                }
            }, 1000);
        }
    });
    let disposable = vscode.commands.registerCommand('cursor-agent-extension.listenFeedback', () => {
        try {
            if (fs.existsSync(feedbackFile)) {
                const content = fs.readFileSync(feedbackFile, 'utf-8');
                const messageForChat = buildMessageForChat(content);
                vscode.env.clipboard.writeText(messageForChat);
                vscode.window.showInformationMessage("✅ 反馈已复制到剪贴板，请在 Cursor Chat 中粘贴并发送！");
            } else {
                vscode.window.showInformationMessage("⚠️ 尚无反馈文件，请先执行 Skill 生成 agent_feedback.txt（兼容旧名 cursor_feedback.txt）");
            }
        } catch (e) {
            vscode.window.showErrorMessage(`❌ 读取失败：${e.message}`);
        }
    });
    context.subscriptions.push(disposable, { dispose: () => watcher.close() });
    vscode.window.showInformationMessage(`✅ Cursor Agent 反馈插件已激活，监听 ${path.basename(feedbackFile)}，反馈将复制到剪贴板并提示粘贴到 Chat。`);
}

function deactivate() {
    vscode.window.showInformationMessage("❌ Cursor Agent插件已关闭！");
}

module.exports = { activate, deactivate };
