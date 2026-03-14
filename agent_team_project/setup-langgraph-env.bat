@echo off
REM LangGraph 独立后端 — 一键安装 + 自检（Windows）
REM 用法：在 agent_team_project 目录下双击运行，或在 cmd 中执行 setup-langgraph-env.bat

set ROOT=%~dp0
if "%ROOT:~-1%"=="\" set ROOT=%ROOT:~0,-1%
cd /d "%ROOT%"

set VENV_DIR=.venv

echo ==========================================
echo LangGraph 前置环境 — 一键安装 + 自检
echo ==========================================
echo 工作目录: %ROOT%
echo.

echo [1/4] 检查 Python 版本...
python --version 2>nul || python3 --version 2>nul
if errorlevel 1 (
    echo 错误: 未找到 python 或 python3，请先安装 Python 3.9+
    pause
    exit /b 1
)
echo   已通过
echo.

echo [2/4] 虚拟环境...
if not exist "%VENV_DIR%" (
    echo    创建 %VENV_DIR% ...
    python -m venv "%VENV_DIR%" 2>nul || python3 -m venv "%VENV_DIR%"
    echo    已创建 %VENV_DIR%
) else (
    echo    已存在 %VENV_DIR%，跳过创建
)
echo.

echo [3/4] 安装必装包...
"%ROOT%\%VENV_DIR%\Scripts\pip.exe" install -q --upgrade pip
"%ROOT%\%VENV_DIR%\Scripts\pip.exe" install "langgraph>=0.2.0" "fastapi>=0.110.0" "uvicorn[standard]>=0.27.0" "pydantic>=2.0" "slowapi>=0.1.0" "python-multipart>=0.0.5"
echo    安装完成
echo.

echo [4/4] 自检...
"%ROOT%\%VENV_DIR%\Scripts\python.exe" -c "import langgraph, fastapi, uvicorn, pydantic, slowapi; print('   全部依赖已就绪。')"
if errorlevel 1 (
    echo 自检未通过，请检查上述错误。
    pause
    exit /b 1
)
echo.

echo ------------------------------------------
echo 后续使用：
echo   激活虚拟环境: %VENV_DIR%\Scripts\activate
echo   启动后端服务: 在激活后执行 uvicorn langgraph_backend.server:app
echo ------------------------------------------
pause
