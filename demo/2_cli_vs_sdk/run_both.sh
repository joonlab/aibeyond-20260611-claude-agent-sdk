#!/usr/bin/env bash
# 데모 ② — CLI vs SDK 나란히 비교
# 같은 프롬프트(prompt.txt) → 같은 결과, 둘 다 구독(OAuth)으로.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="/Users/joon/Desktop/10_프로젝트/날짜별/2026/20260529_claude-adk-sdk-tutorial/venv"
cd "$HERE"

echo ""
echo "########################################################"
echo "#  같은 프롬프트 → 같은 결과, CLI 와 SDK 모두 구독(OAuth)  #"
echo "#  프롬프트: $(cat prompt.txt)"
echo "########################################################"

echo ""
echo "=== CLI ==="
echo "\$ claude -p \"\$(cat prompt.txt)\" --allowedTools Read"
echo "--------------------------------------------------------"
bash "$HERE/run_cli.sh"

echo ""
echo "=== SDK ==="
echo "\$ python3 run_sdk.py   (apiKeySource 출력에 주목 → 'none')"
echo "--------------------------------------------------------"
# shellcheck disable=SC1091
source "$VENV/bin/activate"
env -u ANTHROPIC_API_KEY python3 "$HERE/run_sdk.py"

echo ""
echo "########################################################"
echo "#  결론: 같은 버그를 같게 보고. SDK 는 apiKeySource='none'  #"
echo "#  = API 키가 아니라 제 구독으로 돌고 있는 겁니다.          #"
echo "########################################################"
