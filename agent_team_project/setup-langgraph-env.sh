#!/usr/bin/env bash
# LangGraph 独立后端 — 一键安装 + 自检
# 用法：在 agent_team_project 目录下执行 bash setup-langgraph-env.sh
#       或从任意目录执行 bash /path/to/agent_team_project/setup-langgraph-env.sh

set -e

# 脚本所在目录 = agent_team_project 根目录
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
cd "$ROOT"

VENV_DIR=".venv"
REQUIRED_PACKAGES=(
    "langgraph>=0.2.0"
    "fastapi>=0.110.0"
    "uvicorn[standard]>=0.27.0"
    "pydantic>=2.0"
    "slowapi>=0.1.0"
    "python-multipart>=0.0.5"
    "langchain-core>=0.3.0"
    "langchain-openai>=0.2.0"
)

echo "=========================================="
echo "LangGraph 前置环境 — 一键安装 + 自检"
echo "=========================================="
echo "工作目录: $ROOT"
echo ""

# 1. 检查 Python 版本
echo "[1/4] 检查 Python 版本..."
if ! command -v python3 &>/dev/null; then
    echo "错误: 未找到 python3，请先安装 Python 3.9+"
    exit 1
fi
PY_VERSION=$(python3 -c "import sys; v=sys.version_info; print(f'{v.major}.{v.minor}.{v.micro}')")
PY_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
PY_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")
if [[ "$PY_MAJOR" -lt 3 ]] || [[ "$PY_MAJOR" -eq 3 && "$PY_MINOR" -lt 9 ]]; then
    echo "错误: 需要 Python 3.9+，当前为 $PY_VERSION"
    exit 1
fi
echo "  已通过: Python $PY_VERSION"
echo ""

# 2. 创建虚拟环境（若不存在）
echo "[2/4] 虚拟环境..."
if [[ ! -d "$VENV_DIR" ]]; then
    echo "   创建 $VENV_DIR ..."
    python3 -m venv "$VENV_DIR"
    echo "   已创建 $VENV_DIR"
else
    echo "   已存在 $VENV_DIR，跳过创建"
fi
echo ""

# 3. 安装依赖
echo "[3/4] 安装必装包..."
# 使用 venv 内的 pip，避免依赖系统/用户 site-packages
"$ROOT/$VENV_DIR/bin/pip" install --quiet --upgrade pip
"$ROOT/$VENV_DIR/bin/pip" install "${REQUIRED_PACKAGES[@]}"
echo "   安装完成"
echo ""

# 4. 自检
echo "[4/4] 自检（导入关键模块）..."
"$ROOT/$VENV_DIR/bin/python3" -c '
import sys
checks = [
    ("langgraph", "langgraph"),
    ("fastapi", "fastapi"),
    ("uvicorn", "uvicorn"),
    ("pydantic", "pydantic"),
    ("slowapi", "slowapi"),
    ("langchain_openai", "langchain_openai"),
]
failed = []
for name, mod in checks:
    try:
        __import__(mod)
        v = getattr(__import__(mod), "__version__", "?")
        print(f"   {name}: {v}")
    except ImportError as e:
        print(f"   {name}: 导入失败 - {e}")
        failed.append(name)
if failed:
    print("\n自检未通过，请检查上述错误。")
    sys.exit(1)
print("\n全部依赖已就绪。")
'
echo ""

# 可选：检查 .env 与 runtime_config.json
echo "------------------------------------------"
echo "可选文件检查:"
[[ -f "$ROOT/.env" ]] && echo "   .env: 存在" || echo "   .env: 不存在（若需 API 密钥请自行创建）"
[[ -f "$ROOT/runtime_config.json" ]] && echo "   runtime_config.json: 存在" || echo "   runtime_config.json: 不存在"
echo "------------------------------------------"
echo ""
echo "后续使用："
echo "  激活虚拟环境: source $ROOT/$VENV_DIR/bin/activate"
echo "  启动后端服务: uvicorn langgraph_backend.server:app  # 需先实现 langgraph_backend 模块"
echo ""
