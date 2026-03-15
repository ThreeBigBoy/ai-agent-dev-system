#!/usr/bin/env bash
# LangGraph 后端启动脚本（持久化 AGENT_TEAM_PROJECT_ROOT + 启动前依赖检查）
# 用法：在 agent_team_project 目录下执行 ./start-langgraph-backend.sh
#       或从任意目录执行 bash /path/to/agent_team_project/start-langgraph-backend.sh

set -e

# 脚本所在目录 = agent_team_project
AGENT_TEAM_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
# 本仓项目根 = ai-agent-dev-system（agent_team_project 的上一级）
export AGENT_TEAM_PROJECT_ROOT="$(cd "$AGENT_TEAM_ROOT/.." && pwd)"

VENV_PYTHON="$AGENT_TEAM_ROOT/.venv/bin/python3"
if [[ ! -x "$VENV_PYTHON" ]]; then
    echo "错误: 未找到 $AGENT_TEAM_ROOT/.venv，请先执行依赖安装："
    echo "  cd $AGENT_TEAM_ROOT && bash setup-langgraph-env.sh"
    exit 1
fi

# 启动前依赖检查（pre-flight）：避免启动后 executor 报「未安装 langchain-openai」
echo "检查运行依赖..."
if ! "$VENV_PYTHON" -c "
import sys
for mod in ('langchain_openai', 'langgraph'):
    try:
        __import__(mod)
    except ImportError as e:
        print(f'缺少依赖: {mod}', file=sys.stderr)
        sys.exit(1)
" 2>/dev/null; then
    echo "错误: 当前 .venv 缺少 executor 所需依赖（如 langchain-openai、langgraph）。"
    echo "请先执行："
    echo "  cd $AGENT_TEAM_ROOT && bash setup-langgraph-env.sh"
    echo "或："
    echo "  cd $AGENT_TEAM_ROOT && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

echo "AGENT_TEAM_PROJECT_ROOT=$AGENT_TEAM_PROJECT_ROOT"
echo "启动 LangGraph 后端 (uvicorn) ..."
exec "$VENV_PYTHON" -m uvicorn langgraph_backend.server:app --host 127.0.0.1 --port 8000
