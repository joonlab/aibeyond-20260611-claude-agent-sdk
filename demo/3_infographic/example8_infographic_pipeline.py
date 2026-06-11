"""
Phase 4 · Example 8 — 3-Skill 멀티스텝 인포그래픽 파이프라인
================================================================

3개의 사용자 skill을 SDK가 자동 발동시키는 가장 응용된 시나리오:

  [STEP 1] youtube-download    → 영상 mp3 다운로드 (또는 기존 파일 재사용)
  [STEP 2] elevenlabs-stt      → mp3를 한국어 텍스트로 전사
  [STEP 3] (Claude 요약)        → 전사본에서 핵심 18가지 기능 추출
  [STEP 4] openai-gpt-image-2  → 한국어 인포그래픽 PNG 생성

→ 하나의 SDK 호출로 4단계 파이프라인이 자율 진행.

대상 영상: https://youtu.be/86B_oGCkyMs
         "코덱스 18가지 필수 기능 12분 정리" (코드팩토리)
"""
# === OAuth 인증 부트스트랩 (포팅 시 자동 삽입; 이 블록만 원본과 다름) ===
import os as _os, sys as _sys
_d = _os.path.dirname(_os.path.abspath(__file__))
while _d != "/" and not _os.path.exists(_os.path.join(_d, "_auth.py")):
    _d = _os.path.dirname(_d)
_sys.path.insert(0, _d)
import _auth  # noqa: E402,F401  CLAUDE_CODE_OAUTH_TOKEN 주입 + ANTHROPIC_API_KEY 제거
# === /부트스트랩 ===

import anyio
from pathlib import Path
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    SystemMessage,
    AssistantMessage,
    TextBlock,
    ToolUseBlock,
    ResultMessage,
)


HERE = Path(__file__).resolve().parent
WORKDIR = HERE / "output"
# 입력 mp3: 원본 튜토리얼 폴더의 파일을 재사용(읽기 전용)
EXISTING_MP3 = Path(
    "/Users/joon/Desktop/10_프로젝트/날짜별/2026/20260529_claude-adk-sdk-tutorial/"
    "phase4_harness_in_sdk/yt_downloads/코덱스 18가지 필수 기능 12분 정리.mp3"
)
VIDEO_URL = "https://youtu.be/86B_oGCkyMs"


async def main():
    WORKDIR.mkdir(parents=True, exist_ok=True)

    options = ClaudeAgentOptions(
        setting_sources=["user"],
        # 3개 skill 동시 활성화
        skills=[
            "youtube-download",
            "elevenlabs-stt",
            "openai-gpt-image-2",
        ],
        # skill 내부 script 실행에 필요한 도구들
        allowed_tools=["Read", "Write", "Bash", "Glob"],
        cwd=str(WORKDIR),
        system_prompt=(
            "너는 멀티미디어 파이프라인 오케스트레이터다. "
            "다음 4단계를 자율적으로 진행한다:\n"
            "1) mp3가 이미 있으면 재사용, 없으면 youtube-download skill로 다운로드.\n"
            "2) elevenlabs-stt skill로 mp3를 한국어로 전사. 결과는 .txt 파일.\n"
            "3) 전사본을 읽고 영상의 핵심 18가지 항목을 추출하여 인포그래픽 디자인 프롬프트 작성. "
            "프롬프트는 영어로 작성하되, 인포그래픽 안의 텍스트는 한국어로 표시되도록 지시.\n"
            "4) openai-gpt-image-2 skill로 그 프롬프트를 사용해 인포그래픽 PNG 생성. "
            "size는 1024x1536(세로 인포그래픽 비율), quality=medium.\n\n"
            "각 단계 결과를 한 줄로 보고하며 진행. 모든 산출물은 작업 폴더에 저장."
        ),
    )

    skills_activated = []
    tool_calls = []

    async with ClaudeSDKClient(options=options) as client:
        prompt = (
            f"다음 영상을 한국어 인포그래픽으로 요약해줘.\n"
            f"URL: {VIDEO_URL}\n"
            f"이미 다운받은 mp3가 여기 있어 재사용 가능: {EXISTING_MP3}\n"
            f"작업 폴더(여기에 저장): {WORKDIR}\n\n"
            f"진행:\n"
            f" 1) mp3 확보 (기존 재사용)\n"
            f" 2) elevenlabs-stt로 전사 → transcript.txt\n"
            f" 3) 전사본에서 18가지 핵심 기능 추출 → summary.md\n"
            f" 4) openai-gpt-image-2로 한국어 인포그래픽 PNG 생성 → infographic.png\n"
            f"인포그래픽 디자인 가이드: 깔끔한 미니멀, 한국어 제목 큰 글씨, "
            f"각 기능을 아이콘+짧은 한국어 설명 형식으로 배치, 색상은 차분한 톤(네이비/그레이/포인트 컬러 1개)."
        )
        await client.query(prompt)

        async for msg in client.receive_response():
            if isinstance(msg, SystemMessage) and msg.subtype == "init":
                skills = msg.data.get("skills", [])
                for s in ["youtube-download", "elevenlabs-stt", "openai-gpt-image-2"]:
                    if s in skills:
                        skills_activated.append(s)
                print(f"[init] 활성화 skill: {skills_activated}")

            elif isinstance(msg, AssistantMessage):
                for b in msg.content:
                    if isinstance(b, TextBlock):
                        # 너무 길지 않게
                        text = b.text
                        if len(text) > 500:
                            text = text[:500] + " ..."
                        print(f"[assistant] {text}")
                    elif isinstance(b, ToolUseBlock):
                        tool_calls.append(b.name)
                        if b.name == "Bash":
                            cmd = b.input.get("command", "")[:150]
                            print(f"  [Bash] {cmd}")
                        elif b.name == "Read":
                            print(f"  [Read] {b.input.get('file_path','')[:120]}")
                        elif b.name == "Write":
                            print(f"  [Write] {b.input.get('file_path','')[:120]}")
                        elif b.name == "Skill":
                            print(f"  [Skill 활성화] {b.input.get('skill','?')}")
                        else:
                            print(f"  [{b.name}] {str(b.input)[:120]}")

            elif isinstance(msg, ResultMessage):
                print(f"\n=== Run stats ===")
                print(f"duration: {msg.duration_ms / 1000:.1f}s")
                print(f"cost:     ${msg.total_cost_usd:.4f}")
                print(f"turns:    {msg.num_turns}")
                print(f"전체 tool 호출 ({len(tool_calls)}): {tool_calls}")

    # 결과물 검증
    print(f"\n=== 파이프라인 산출물 ({WORKDIR}) ===")
    for f in sorted(WORKDIR.iterdir()):
        if f.is_file():
            size_kb = f.stat().st_size / 1024
            unit = "MB" if size_kb > 1024 else "KB"
            size_val = size_kb / 1024 if size_kb > 1024 else size_kb
            print(f"  ✓ {f.name}  ({size_val:.2f} {unit})")

    print(f"\n=== 종합 ===")
    print(f"  활성화된 3-skill: {skills_activated}")
    print(f"  Skill 도구 호출: {tool_calls.count('Skill')}회")
    has_infographic = any((WORKDIR / n).exists() for n in ["infographic.png", "infographic.jpg"])
    print(f"  인포그래픽 생성: {'✓' if has_infographic else '✗'}")


anyio.run(main)
