"""데모용 서버 런처 (OAuth 모드)
================================
backend.py 본문은 원본 그대로 유지한다. 단, 원본 `__main__` 가드에는
`if not ANTHROPIC_API_KEY: sys.exit(1)` 가 있어 OAuth(키 제거) 모드에서는
직접 실행 시 서버가 뜨지 않는다(RESULTS.md §4 ³ 참조).

이 런처는 backend.py의 `app`만 import 해서(=`_auth` 부트스트랩이 먼저 돌아
ANTHROPIC_API_KEY 제거 + OAuth 주입) `__main__` 가드를 건너뛰고 uvicorn 을
직접 띄운다. 본문 로직은 일절 손대지 않는다.
"""
import uvicorn
from backend import app  # import 시 backend.py 상단의 _auth 부트스트랩이 실행됨

if __name__ == "__main__":
    print("=" * 56)
    print("  Research 웹앱 (OAuth/구독 토큰 기반)")
    print("  → 브라우저에서 http://localhost:8765 열기")
    print("  → 종료: Ctrl+C")
    print("=" * 56, flush=True)
    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="info")
