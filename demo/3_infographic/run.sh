#!/usr/bin/env bash
# 데모 ③ — 3-Skill 인포그래픽 파이프라인 (백그라운드 실행 권장)
# youtube-download → elevenlabs-stt → (요약) → openai-gpt-image-2
# 단일 SDK 호출로 4단계 자율 진행. 약 4분 소요.
#
# 인증: Claude 는 OAuth(구독) — ANTHROPIC_API_KEY 만 제거.
#       단, skill 내부가 쓰는 ELEVENLABS_API_KEY / OPENAI_API_KEY 는 보존해야 함.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="/Users/joon/Desktop/10_프로젝트/날짜별/2026/20260529_claude-adk-sdk-tutorial/venv"
LOG="$HERE/run.log"

# 필수 외부 키 점검 (Claude 인증과 별개로 skill 들이 사용)
missing=0
if [ -z "${ELEVENLABS_API_KEY:-}" ]; then echo "[run] ⚠️  ELEVENLABS_API_KEY 미설정 (STEP2 전사 실패함)"; missing=1; fi
if [ -z "${OPENAI_API_KEY:-}" ];     then echo "[run] ⚠️  OPENAI_API_KEY 미설정 (STEP4 이미지생성 실패함)"; missing=1; fi
if [ "$missing" = 1 ]; then
  echo "[run] 위 키들을 export 한 뒤 다시 실행하세요. (Claude 는 OAuth 라 키 불필요)"
fi

# shellcheck disable=SC1091
source "$VENV/bin/activate"

echo "[run] 백그라운드로 파이프라인 시작. 로그: $LOG"
echo "[run] 진행 확인:   tail -f \"$LOG\""
echo "[run] 산출물:      $HERE/output/  (infographic.png 가 최종물)"

# ANTHROPIC_API_KEY 만 제거(OAuth 강제), ELEVENLABS/OPENAI 는 현재 환경 그대로 상속.
cd "$HERE"
nohup env -u ANTHROPIC_API_KEY python3 example8_infographic_pipeline.py \
  > "$LOG" 2>&1 &

echo "[run] PID=$! 로 백그라운드 실행 중. (약 4분)"
