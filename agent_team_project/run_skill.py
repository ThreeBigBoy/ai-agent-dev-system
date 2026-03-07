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
DECISION_FILE = BASE_DIR / "cursor_decision.json"
SKILL_SCRIPT = BASE_DIR / "dynamic_agent_skill.py"
FEEDBACK_FILE = BASE_DIR / "cursor_feedback.txt"
TIMEOUT = RUNTIME_CONFIG["run_skill"]["timeout_seconds"]

def read_cursor_decision():
    if not DECISION_FILE.exists():
        logger.error(f"❌ 未找到决策文件：{DECISION_FILE}")
        logger.info("请先让Cursor Chat生成决策并写入该文件")
        return None
    try:
        with open(DECISION_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
        json.loads(content)
        return content
    except json.JSONDecodeError:
        logger.error(f"❌ {DECISION_FILE} 文件内容不是合法JSON，请让Cursor重新生成")
        return None
    except Exception as e:
        logger.error(f"❌ 读取决策文件失败：{str(e)}")
        return None

def trigger_skill(decision_json):
    cmd = [sys.executable, str(SKILL_SCRIPT), decision_json]
    logger.info(f"🚀 执行Skill命令：{cmd[0]} {SKILL_SCRIPT.name} <decision_json>")
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
            if FEEDBACK_FILE.exists():
                logger.info(f"📄 反馈结果已写入：{FEEDBACK_FILE}，插件将复制到剪贴板并提示粘贴到 Chat")
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
    decision_json = read_cursor_decision()
    if not decision_json:
        logger.info("=============== Skill执行终止 ===============")
        return
    success = trigger_skill(decision_json)
    if success:
        logger.info("🎉 Skill执行完成！请将剪贴板中的反馈粘贴到 Cursor Chat 并发送，或等待插件提示后粘贴")
    else:
        logger.error("❌ Skill执行失败，请查看agent_skill.log日志排查问题")
    logger.info("=============== Skill执行流程结束 ===============")

if __name__ == "__main__":
    main()
