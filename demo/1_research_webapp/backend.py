"""
Phase 3 — Research Web App (영상 마지막 부분 재현)
====================================================

구조:
  FastAPI 백엔드 + SSE(Server-Sent Events) 스트리밍 + 정적 HTML 프론트엔드.
  사용자가 질문 → ClaudeSDKClient가 WebSearch/WebFetch로 리서치 → 추론/도구호출/결과를
  토큰 단위로 SSE로 푸시 → 프론트엔드가 실시간 렌더링.

실행:
  $ source ../venv/bin/activate && source ../.env
  $ export ANTHROPIC_API_KEY=...
  $ python3 backend.py
  → 브라우저에서 http://localhost:8765 접속

엔드포인트:
  GET  /              → index.html 서빙
  GET  /api/research?q=<질문>  → SSE 스트림 (event: chunk/tool/done)
"""
# === OAuth 인증 부트스트랩 (포팅 시 자동 삽입; 이 블록만 원본과 다름) ===
import os as _os, sys as _sys
_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != "/" and not _os.path.exists(_os.path.join(_d, "_auth.py")):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)
import _auth  # noqa: E402,F401  CLAUDE_CODE_OAUTH_TOKEN 주입 + ANTHROPIC_API_KEY 제거
# === /부트스트랩 ===

import json
import os
import sys
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from sse_starlette.sse import EventSourceResponse

from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
    ThinkingBlock,
    ToolUseBlock,
    ResultMessage,
    SystemMessage,
)

HERE = Path(__file__).resolve().parent
app = FastAPI(title="Claude SDK Research Webapp")


@app.get("/")
async def index():
    return FileResponse(HERE / "frontend.html")


@app.get("/api/research")
async def research(request: Request, q: str):
    """질문 q에 대해 ClaudeSDKClient로 리서치하고 결과를 SSE로 스트리밍."""

    async def event_stream():
        # 시작 알림
        yield {"event": "status", "data": json.dumps({"msg": "🔌 SDK 연결 중..."})}

        options = ClaudeAgentOptions(
            setting_sources=[],
            allowed_tools=["WebSearch", "WebFetch"],
            system_prompt=(
                "너는 시니어 리서치 분석가다. "
                "사용자의 질문에 대해 WebSearch로 최신 정보를 찾고, "
                "WebFetch로 신뢰할 만한 출처를 직접 확인한 뒤, "
                "마지막에 출처 링크를 포함한 마크다운 보고서로 정리한다. "
                "추측 금지. 도구로 확인 못 한 건 '확인 불가'."
            ),
        )

        try:
            async with ClaudeSDKClient(options=options) as client:
                yield {"event": "status", "data": json.dumps({"msg": "🔍 리서치 시작"})}
                await client.query(q)

                async for msg in client.receive_response():
                    if await request.is_disconnected():
                        break

                    if isinstance(msg, SystemMessage):
                        # init 메타데이터 — 모델 정보만 흘려보냄
                        if msg.subtype == "init":
                            yield {
                                "event": "status",
                                "data": json.dumps({
                                    "msg": f"⚡ 모델: {msg.data.get('model','?')}"
                                })
                            }

                    elif isinstance(msg, AssistantMessage):
                        for b in msg.content:
                            if isinstance(b, ThinkingBlock):
                                # 영상의 "streams its reasoning"
                                yield {
                                    "event": "thinking",
                                    "data": json.dumps({"text": b.thinking[:200]}),
                                }
                            elif isinstance(b, ToolUseBlock):
                                yield {
                                    "event": "tool",
                                    "data": json.dumps({
                                        "name": b.name,
                                        "input": b.input,
                                    }),
                                }
                            elif isinstance(b, TextBlock):
                                yield {
                                    "event": "chunk",
                                    "data": json.dumps({"text": b.text}),
                                }

                    elif isinstance(msg, ResultMessage):
                        yield {
                            "event": "done",
                            "data": json.dumps({
                                "duration_ms": msg.duration_ms,
                                "cost_usd": msg.total_cost_usd,
                                "num_turns": msg.num_turns,
                            }),
                        }
                        return
        except Exception as e:
            yield {"event": "error", "data": json.dumps({"msg": str(e)})}

    return EventSourceResponse(event_stream())


@app.get("/api/health")
async def health():
    has_key = bool(os.environ.get("ANTHROPIC_API_KEY"))
    return JSONResponse({"ok": True, "api_key_set": has_key})


if __name__ == "__main__":
    import uvicorn

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("⚠️  ANTHROPIC_API_KEY 미설정. ../.env 로드 필요", file=sys.stderr)
        sys.exit(1)

    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="info")
