#!/usr/bin/env bash
# 데모 ② — CLI 쪽 (claude -p, 인터랙티브 구독 인증 그대로 사용)
# prompt.txt 의 동일 프롬프트를 Claude Code CLI 로 실행.
# CLI 는 로그인된 구독 세션(OAuth)을 그대로 쓰므로 별도 키 설정이 필요 없다.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

PROMPT="$(cat prompt.txt)"

# ANTHROPIC_API_KEY 가 셸에 떠 있으면 종량제로 샐 수 있으므로 제거하고 실행.
# CLI 는 ~/.claude 의 구독 로그인(OAuth)으로 인증한다.
exec env -u ANTHROPIC_API_KEY claude -p "$PROMPT" --allowedTools "Read"
