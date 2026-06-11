#!/usr/bin/env bash
# 데모 ① Research 웹앱 — OAuth(구독 토큰) 기반 FastAPI + SSE 스트리밍
# 포트 8765 에서 기동. 브라우저로 http://localhost:8765 접속해 질문 입력.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="/Users/joon/Desktop/10_프로젝트/날짜별/2026/20260529_claude-adk-sdk-tutorial/venv"

# venv 활성화
# shellcheck disable=SC1091
source "$VENV/bin/activate"

# 안전: 셸에 ANTHROPIC_API_KEY 가 떠 있어도 제거하고 띄운다(OAuth 강제).
# (_auth.py 가 프로세스 내에서 한 번 더 제거하지만 셸 레벨에서도 차단)
echo "[run] 포트 8765 점검..."
if lsof -nP -iTCP:8765 -sTCP:LISTEN >/dev/null 2>&1; then
  echo "[run] ⚠️  포트 8765 가 이미 사용 중입니다. 기존 프로세스를 종료하세요:"
  lsof -nP -iTCP:8765 -sTCP:LISTEN
  exit 1
fi

echo "[run] OAuth 모드로 서버 기동 (ANTHROPIC_API_KEY 제거)..."
cd "$HERE"
exec env -u ANTHROPIC_API_KEY python3 _server.py
