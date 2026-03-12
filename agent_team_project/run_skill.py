import os
import json
import subprocess
import time
import logging
import sys
from pathlib import Path

from runtime_config import load_runtime_config

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger("RunSkill")

BASE_DIR = Path(__file__).resolve().parent
RUNTIME_CONFIG = load_runtime_config()
SKILL_SCRIPT = BASE_DIR / "dynamic_agent_skill.py"
TIMEOUT = RUNTIME_CONFIG["run_skill"]["timeout_seconds"]


def _workspace_root() -> Path | None:
    root = os.environ.get("AGENT_TEAM_PROJECT_ROOT", "").strip()
    if root and Path(root).is_dir():
        return Path(root)
    return None


def _decision_candidates() -> list[Path]:
    roots = []
    workspace_root = _workspace_root()
    if workspace_root:
        roots.append(workspace_root)
    roots.append(BASE_DIR)
    candidates = []
    for root in roots:
        candidates.append(root / "agent_decision.json")
    return candidates


def _feedback_candidates() -> list[Path]:
    roots = []
    workspace_root = _workspace_root()
    if workspace_root:
        roots.append(workspace_root)
    roots.append(BASE_DIR)
    candidates = []
    for root in roots:
        candidates.append(root / "agent_feedback.txt")
    return candidates


def read_agent_decision():
    """返回 (决策 JSON 内容, 决策文件路径)；若无有效决策则返回 (None, None)。"""
    for decision_file in _decision_candidates():
        if not decision_file.exists():
            continue
        try:
            with open(decision_file, "r", encoding="utf-8") as f:
                content = f.read().strip()
            if not content:
                logger.error(f"❌ {decision_file} 文件为空，请让宿主重新写入决策")
                continue
            json.loads(content)
            logger.info(f"📥 使用决策文件：{decision_file}")
            return content, str(decision_file.resolve())
        except json.JSONDecodeError:
            logger.error(f"❌ {decision_file} 文件内容不是合法JSON，请让宿主重新生成")
            return None, None
        except Exception as e:
            logger.error(f"❌ 读取决策文件失败：{decision_file}，原因：{str(e)}")
            return None, None
    logger.error(f"❌ 未找到决策文件，已检查：{_decision_candidates()}")
    logger.info("请先让宿主侧主 Agent 生成决策并写入 decision sink")
    return None, None

def trigger_skill(decision_file_path):
    """传入决策文件绝对路径，由 skill 脚本从文件读取，避免命令行传大段 JSON。"""
    cmd = [sys.executable, str(SKILL_SCRIPT), decision_file_path]
    logger.info(f"🚀 执行Skill命令：{cmd[0]} {SKILL_SCRIPT.name} <决策文件路径>")
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8",
            cwd=BASE_DIR
        )
        for line in process.stdout:
            logger.info(f"📝 Skill输出：{line.strip()}")
        process.wait(timeout=TIMEOUT)
        if process.returncode == 0:
            logger.info("✅ Skill执行成功！")
            time.sleep(1)
            feedbacks = [path for path in _feedback_candidates() if path.exists()]
            if feedbacks:
                logger.info(f"📄 反馈结果已写入：{feedbacks}")
            return True
        error = process.stderr.read()
        logger.error(f"❌ Skill执行失败：{error[:200]}...")
        return False
    except subprocess.TimeoutExpired:
        process.kill()
        logger.error(f"❌ Skill执行超时（{TIMEOUT}秒），已终止")
        return False
    except Exception as e:
        logger.error(f"❌ 触发Skill失败：{str(e)}")
        return False

def main():
    logger.info("=============== 开始执行Agent团队Skill ===============")
    decision_json, decision_path = read_agent_decision()
    if not decision_json or not decision_path:
        logger.info("=============== Skill执行终止 ===============")
        return
    success = trigger_skill(decision_path)
    if success:
        logger.info("🎉 Skill执行完成！请将剪贴板中的反馈粘贴回当前主 Agent 会话，或等待宿主侧提示后继续")
    else:
        logger.error("❌ Skill执行失败，请查看agent_skill.log日志排查问题")
    logger.info("=============== Skill执行流程结束 ===============")

if __name__ == "__main__":
    main()
