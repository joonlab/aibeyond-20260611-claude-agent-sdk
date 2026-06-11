"""OAuth 인증 부트스트랩 (자가완결)
====================================

이 모듈을 `import` 하기만 하면:
  1) 같은 폴더의 `.env` 를 수동 파싱(python-dotenv 비의존)해
     CLAUDE_CODE_OAUTH_TOKEN 을 os.environ 에 주입한다.
  2) os.environ.pop("ANTHROPIC_API_KEY", None) 으로 API 키를 강제 제거한다.
     → claude_agent_sdk 가 띄우는 Claude Code CLI 서브프로세스가
       API 키(종량제) 대신 OAuth(구독) 토큰으로만 인증하도록 만든다.
  3) CLAUDE_CODE_OAUTH_TOKEN 이 어디에도 없으면 명확한 에러로 중단한다.

원본 튜토리얼(루트 .env = ANTHROPIC_API_KEY)을 일절 건드리지 않고
oauth_version/ 안에서만 인증 출처를 OAuth 로 바꾸기 위한 장치다.
"""
import os
from pathlib import Path

_ENV_PATH = Path(__file__).resolve().parent / ".env"


def _parse_env(path: Path) -> dict:
    """KEY=VALUE 형식 .env 를 수동 파싱(따옴표/주석/공백 처리)."""
    out = {}
    if not path.exists():
        return out
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip().strip('"').strip("'").strip()
        if key:
            out[key] = val
    return out


def _bootstrap():
    env = _parse_env(_ENV_PATH)

    # 1) OAuth 토큰 확보: .env 우선, 없으면 기존 환경변수 허용
    token = env.get("CLAUDE_CODE_OAUTH_TOKEN") or os.environ.get(
        "CLAUDE_CODE_OAUTH_TOKEN"
    )
    if not token:
        raise RuntimeError(
            "CLAUDE_CODE_OAUTH_TOKEN 이 없습니다. "
            f"{_ENV_PATH} 에 'CLAUDE_CODE_OAUTH_TOKEN=sk-ant-oat01-...' 를 설정하세요. "
            "(claude setup-token 으로 발급)"
        )
    os.environ["CLAUDE_CODE_OAUTH_TOKEN"] = token

    # 2) API 키 강제 제거 → 종량제 경로 차단, OAuth(구독)로만 인증
    removed = os.environ.pop("ANTHROPIC_API_KEY", None)

    # 3) 혹시 .env 에 API 키가 섞여 있어도 환경에 주입하지 않음(방어)
    #    (env dict 의 ANTHROPIC_API_KEY 는 의도적으로 무시)

    masked = f"{token[:18]}***" if len(token) > 18 else "***"
    print(
        f"[_auth] OAuth 인증 활성화: CLAUDE_CODE_OAUTH_TOKEN={masked} "
        f"| ANTHROPIC_API_KEY {'제거됨' if removed else '원래 없음'}",
        flush=True,
    )
    return token, removed


_TOKEN, _REMOVED_API_KEY = _bootstrap()
