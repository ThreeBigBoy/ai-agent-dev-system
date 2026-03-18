#!/usr/bin/env bash
# 联调/冒烟测试：在 LangGraph 后端已启动（默认 http://127.0.0.1:8000）时执行。
# 用法: ./scripts/smoke_http.sh [BASE_URL]
set -e
BASE="${1:-http://127.0.0.1:8000}"
CHANGE_ID="deepen-langgraph-v2-11-1"

echo "=== 1. GET /health ==="
curl -s "$BASE/health" | head -5
echo ""

echo "=== 2. POST /run (可能返回 waiting_hc0 或继续至 waiting_hc7) ==="
RUN=$(curl -s -X POST "$BASE/run" -H "Content-Type: application/json" -d "{\"change_id\":\"$CHANGE_ID\"}")
echo "$RUN" | head -20
STATUS=$(echo "$RUN" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null || echo "")
echo "status: $STATUS"

if [ -n "$STATUS" ] && [ "$STATUS" = "waiting_hc0" ] || [ "$STATUS" = "waiting_hc2" ] || [ "$STATUS" = "waiting_hc7" ]; then
  echo "=== 3. GET /confirm/pending?change_id=$CHANGE_ID ==="
  curl -s "$BASE/confirm/pending?change_id=$CHANGE_ID" || true
  echo ""
  echo "=== 4. GET /confirm/poll (timeout_seconds=2) ==="
  curl -s "$BASE/confirm/poll?change_id=$CHANGE_ID&timeout_seconds=2" || true
  echo ""
fi

echo "=== smoke_http done ==="
