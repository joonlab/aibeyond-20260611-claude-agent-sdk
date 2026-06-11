"""데모 ② — SDK 쪽 (Claude Agent SDK, OAuth/구독 토큰)
=========================================================
prompt.txt 의 동일 프롬프트를 ClaudeSDKClient 로 실행한다.

핵심 시연 포인트:
  - `_auth` 부트스트랩이 ANTHROPIC_API_KEY 를 제거하고 CLAUDE_CODE_OAUTH_TOKEN 을 주입.
  - SystemMessage(init) 의 `apiKeySource` 를 화면에 출력 → **'none'** 이면
    "API 키가 아니라 구독(OAuth)으로 돌고 있다"는 증거.
  - allowed_tools=["Read"], setting_sources=[] 로 CLI 와 동일 조건 + 환경 격리.
"""
# === OAuth 인증 부트스트랩 (oauth_version 패턴; __file__ 상위로 _auth.py 탐색) ===
import os as _os, sys as _sys
_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != "/" and not _os.path.exists(_os.path.join(_d, "_auth.py")):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)
import _auth  # noqa: E402,F401  CLAUDE_CODE_OAUTH_TOKEN 주입 + ANTHROPIC_API_KEY 제거
# === /부트스트랩 ===

from pathlib import Path

import anyio
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    SystemMessage,
    AssistantMessage,
    TextBlock,
    ResultMessage,
)

HERE = Path(__file__).resolve().parent
PROMPT = (HERE / "prompt.txt").read_text(encoding="utf-8").strip()


async def main():
    options = ClaudeAgentOptions(
        setting_sources=[],           # 사용자 settings 상속 차단 (CLI 와 동일 조건)
        allowed_tools=["Read"],       # Read 만 허용 (CLI 의 --allowedTools Read 와 동일)
        cwd=str(HERE),                # fibonacci.py 가 있는 폴더에서 작업
    )

    api_key_source = None
    async with ClaudeSDKClient(options=options) as client:
        await client.query(PROMPT)

        async for msg in client.receive_response():
            if isinstance(msg, SystemMessage) and msg.subtype == "init":
                api_key_source = msg.data.get("apiKeySource", "?")
                print(f"[init] apiKeySource = {api_key_source!r}  "
                      f"(model={msg.data.get('model','?')})", flush=True)
            elif isinstance(msg, AssistantMessage):
                for b in msg.content:
                    if isinstance(b, TextBlock) and b.text.strip():
                        print(b.text.strip(), flush=True)
            elif isinstance(msg, ResultMessage):
                print(
                    f"\n[stats] {msg.duration_ms/1000:.1f}s "
                    f"/ ${(msg.total_cost_usd or 0):.4f} / {msg.num_turns}턴",
                    flush=True,
                )

    # 발표용 한 줄 요약
    verdict = "구독(OAuth) 경로" if api_key_source == "none" else f"({api_key_source})"
    print(f"\n>>> apiKeySource={api_key_source!r} → {verdict}", flush=True)


anyio.run(main)
