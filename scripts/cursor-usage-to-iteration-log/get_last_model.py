#!/usr/bin/env python3
"""
从 Cursor 用量 API 获取「最近一次请求的模型」，供迭代日志「使用模型」字段使用。
与 Cursor Usage Monitor 插件使用相同数据源：cursor.com API + 本地 token。
用法：python get_last_model.py
输出：stdout 一行，为模型名；失败或无数据时输出占位符。
"""

import os
import sys
import json
import sqlite3
import platform
import base64
import re
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    print("Auto（具体模型未暴露）", end="")
    sys.exit(0)

# 占位符：无具体模型时供 Agent 写入日志
PLACEHOLDER_AUTO = "Auto（具体模型未暴露）"
PLACEHOLDER_UNKNOWN = "—"
API_BASE = "https://cursor.com/api"
EVENTS_ENDPOINT = f"{API_BASE}/dashboard/get-filtered-usage-events"


def get_cursor_db_path() -> Optional[Path]:
    """Cursor state.vscdb 路径（与 Cursor Usage Monitor 一致）。"""
    home = Path.home()
    system = platform.system()
    if system == "Darwin":
        return home / "Library/Application Support/Cursor/User/globalStorage/state.vscdb"
    if system == "Windows":
        return home / "AppData/Roaming/Cursor/User/globalStorage/state.vscdb"
    return home / ".config/Cursor/User/globalStorage/state.vscdb"


def read_token_from_sqlite() -> Optional[str]:
    """从 Cursor 本地 SQLite 读取 cursorAuth/accessToken。"""
    db_path = get_cursor_db_path()
    if not db_path or not db_path.exists():
        return None
    try:
        conn = sqlite3.connect(str(db_path))
        cur = conn.execute(
            "SELECT value FROM ItemTable WHERE key = 'cursorAuth/accessToken'"
        )
        row = cur.fetchone()
        conn.close()
        return row[0].strip() if row and row[0] else None
    except Exception:
        return None


def get_token() -> Optional[str]:
    """优先环境变量，否则从 Cursor SQLite 读取。"""
    token = os.environ.get("CURSOR_SESSION_TOKEN", "").strip()
    if token:
        return token
    return read_token_from_sqlite()


def extract_user_id_from_token(token: str) -> Optional[str]:
    """从 token 解析 userId：user_XXX::jwt 或 JWT payload.sub 中的 user_XXX。"""
    if "::" in token:
        return token.split("::")[0].strip()
    # JWT: base64url decode payload (第二部分)
    parts = token.split(".")
    if len(parts) != 3:
        return None
    try:
        payload_b64 = parts[1]
        payload_b64 += "=" * (4 - len(payload_b64) % 4)
        payload_b64 = payload_b64.replace("-", "+").replace("_", "/")
        payload = json.loads(base64.b64decode(payload_b64).decode())
        sub = payload.get("sub") or payload.get("userId") or ""
        match = re.search(r"user_[A-Za-z0-9]+", str(sub))
        return match.group(0) if match else None
    except Exception:
        return None


def build_cookie_value(token: str, user_id: Optional[str]) -> str:
    """拼成 Cookie：WorkosCursorSessionToken=userId%3A%3Ajwt。"""
    if "::" in token or "%3A%3A" in token:
        return token.replace("::", "%3A%3A") if "%" not in token else token
    if user_id:
        return f"{user_id}%3A%3A{token}"
    return token


def fetch_usage_events(token: str, user_id: Optional[str]) -> Optional[list]:
    """POST get-filtered-usage-events，返回 usageEventsDisplay 列表。"""
    import time
    start_ms = int((time.time() - 86400) * 1000)  # 最近 24h
    end_ms = int(time.time() * 1000)
    cookie_val = build_cookie_value(token, user_id)
    headers = {
        "Cookie": f"WorkosCursorSessionToken={cookie_val}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (compatible; CursorIterationLog/1.0)",
        "Accept": "application/json",
        "Origin": "https://cursor.com",
        "Referer": "https://cursor.com/",
    }
    payload = {
        "teamId": 0,
        "startDate": str(start_ms),
        "endDate": str(end_ms),
        "page": 1,
        "pageSize": 50,
    }
    try:
        r = requests.post(
            EVENTS_ENDPOINT,
            json=payload,
            headers=headers,
            timeout=15,
        )
        if r.status_code != 200:
            return None
        data = r.json()
        events = data.get("usageEventsDisplay") or data.get("usageEventsDisplayDisplay") or []
        return events if isinstance(events, list) else None
    except Exception:
        return None


def get_last_model_from_events(events: list) -> str:
    """从事件列表取最近一条的 model；无或为空则返回占位符。"""
    if not events:
        return PLACEHOLDER_AUTO
    # 按 timestamp 降序（最大为最近）
    sorted_events = sorted(
        events,
        key=lambda e: int(e.get("timestamp") or 0),
        reverse=True,
    )
    model = (sorted_events[0].get("model") or "").strip()
    # 仅将明确无法识别的视为占位符；"default" 为 Cursor API 实际返回值，原样输出便于核对
    if not model or model.lower() in ("auto", "unknown"):
        return PLACEHOLDER_AUTO
    return model


def main() -> None:
    token = get_token()
    if not token:
        print(PLACEHOLDER_UNKNOWN, end="")
        return
    user_id = extract_user_id_from_token(token)
    events = fetch_usage_events(token, user_id)
    if events is None:
        print(PLACEHOLDER_AUTO, end="")
        return
    model = get_last_model_from_events(events)
    print(model, end="")


if __name__ == "__main__":
    main()

