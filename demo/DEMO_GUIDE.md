# 라이브 데모 가이드 — Claude Agent SDK (ai & beyond, 2026-06-11)

> 데모 3종 **전부 OAuth(구독 토큰) 기반**. `ANTHROPIC_API_KEY` 사용 안 함.
> 인증은 `demo/.env` 의 `CLAUDE_CODE_OAUTH_TOKEN` + `demo/_auth.py` 부트스트랩으로 자동 주입.
> venv: `/Users/joon/Desktop/10_프로젝트/날짜별/2026/20260529_claude-adk-sdk-tutorial/venv`

핵심 한 마디(세 데모 공통): **"apiKeySource 가 none — API 키가 아니라 제 구독으로 돌고 있는 겁니다."**

---

## 발표 중 타임라인 배치 (15~20분)

| 시점 | 데모 | 동작 | 소요 |
|---|---|---|---|
| **시작 직후** | ③ 인포그래픽 | 백그라운드로 켜두기 (`3_infographic/run.sh`) | ~4분 (백그라운드) |
| **중반** | ② CLI vs SDK | 같은 프롬프트 → 같은 결과, apiKeySource 차이 강조 | 1~2분 |
| **중후반** | ① Research 웹앱 | 질문 입력 → SSE 스트리밍 → 보고서 | 1~2분 |
| **마무리 직전** | ③ 결과 확인 | `output/infographic.png` 오픈 → "발표하는 동안 영상 1개가 인포그래픽이 됐습니다" | — |

---

## 데모 ① Research 웹앱 (`1_research_webapp/`)

FastAPI + SSE 로 ClaudeSDKClient 의 리서치 과정을 실시간 스트리밍. 신문 스타일 프론트("The Research Daily").

**실행**
```bash
cd demo/1_research_webapp
./run.sh
# → 브라우저에서 http://localhost:8765 열기
# → 종료: Ctrl+C
```

- **예상 소요**: 질문 1건당 20~45초 (WebSearch + WebFetch)
- **예상 비용**: ~$0.06 ~ $0.25 / 질문
- **검증됨**: `/api/health` → `{"ok":true,"api_key_set":false}` (HTTP 200), `GET /` HTTP 200, OAuth 부트스트랩 동작
- **시연 질문 예시**: "2026년 6월 기준 가장 최신 Claude 모델은?" 같이 최신성·출처가 필요한 질문
- **말할 포인트**:
  - "백엔드에 API 키가 하나도 없습니다 — `/api/health` 가 `api_key_set:false`"
  - SSE 5종 이벤트(status/thinking/tool/chunk/done)가 실시간으로 흐르는 것 강조
  - "ClaudeSDKClient 를 그냥 FastAPI 안에 임베드한 것"

**구조 메모**: `run.sh` → `_server.py`(데모용 런처) → `backend.py`(원본 본문 그대로).
원본 `backend.py` 의 `__main__` 가드에 `if not ANTHROPIC_API_KEY: sys.exit(1)` 가 있어
OAuth 모드(키 제거)에서는 직접 실행 시 서버가 안 뜬다. 그래서 `_server.py` 가 `app` 만 import 해
(=`_auth` 부트스트랩 선실행) 가드를 건너뛰고 uvicorn 을 띄운다. 본문 로직은 손대지 않음.

**플랜 B**: 포트 충돌/네트워크 문제 시 — 사전 녹화 GIF 또는 health 응답 스크린샷 사용.
사전 실행 로그 위치: `/tmp/demo1_server.log` (발표 직전 재실행 권장).

---

## 데모 ② CLI vs SDK 나란히 비교 (`2_cli_vs_sdk/`) — **발표 임팩트 핵심**

같은 프롬프트(`prompt.txt`)를 CLI(`claude -p`)와 SDK(`ClaudeSDKClient`)로 각각 실행 →
**같은 버그를 같게 보고**, 그리고 SDK 쪽은 `apiKeySource='none'` 을 화면에 출력.

**실행 (한 번에 둘 다)**
```bash
cd demo/2_cli_vs_sdk
./run_both.sh        # === CLI === 후 === SDK === 순차 출력
```
개별 실행도 가능:
```bash
./run_cli.sh         # claude -p "$(cat prompt.txt)" --allowedTools Read
python3 run_sdk.py   # (venv 활성화 후) apiKeySource 출력에 주목
```

- **공통 프롬프트**: "이 폴더의 fibonacci.py를 읽고 버그를 찾아 한 줄로 보고해줘."
- **대상 코드**: `fibonacci.py` — 의도적 off-by-one (`n=1`일 때 `[0,1]` 2개 반환)
- **예상 소요**: CLI ~15초 + SDK ~12초 = 합쳐서 30초 내외
- **예상 비용**: SDK ~$0.07 (CLI 는 구독 세션)
- **검증됨 (실측)**:
  - SDK: EXIT=0, `apiKeySource = 'none'`, 12.1s / $0.0663, 버그 정확히 발견
  - CLI: EXIT=0, 동일 off-by-one 버그 보고 (표현만 약간 다름, 진단 동일)
- **말할 포인트**:
  - "왼쪽 CLI, 오른쪽 SDK — 같은 프롬프트에 같은 버그를 짚었습니다."
  - **"SDK 출력의 `apiKeySource='none'` 보이시죠? API 키가 아니라 제 구독(OAuth)으로 돈 겁니다."**
  - "SDK 는 결국 Claude Code CLI 를 subprocess 로 띄웁니다 — 그래서 인증도 CLI 와 같은 구독 토큰."

**플랜 B**: 라이브 실행 실패 시 — 아래 사전 실측 결과를 그대로 읽어준다.
```
[init] apiKeySource = 'none'  (model=claude-sonnet-4-6)
**버그:** n=1일 때 seq=[0,1]로 초기화 후 그대로 반환 → return seq[:n] 로 슬라이싱해야 함.
[stats] 12.1s / $0.0663 / 4턴
>>> apiKeySource='none' → 구독(OAuth) 경로
```

---

## 데모 ③ 3-Skill 인포그래픽 파이프라인 (`3_infographic/`)

단일 SDK 호출로 4단계 자율 진행:
`youtube-download` → `elevenlabs-stt` → (Claude 요약) → `openai-gpt-image-2`.
"코덱스 18가지 필수 기능" 영상 mp3 → 한국어 인포그래픽 PNG.

**실행 (발표 시작 직후 백그라운드로)**
```bash
cd demo/3_infographic
./run.sh             # nohup 백그라운드 실행, 로그: run.log
tail -f run.log      # 진행 확인
# 산출물: output/  (infographic.png 가 최종물)
```

- **입력 mp3**: `…/20260529_claude-adk-sdk-tutorial/phase4_harness_in_sdk/yt_downloads/코덱스 18가지 필수 기능 12분 정리.mp3` (재사용, 읽기 전용)
- **출력**: `demo/3_infographic/output/` (transcript.txt, summary.md, design_prompt.txt, infographic.png)
- **예상 소요**: 약 4분 (전사 + 요약 + 이미지 생성)
- **예상 비용**: Claude ~$0.72 + ElevenLabs STT + OpenAI 이미지 생성 (외부 API 별도 과금)
- **인증**:
  - Claude → **OAuth** (`ANTHROPIC_API_KEY` 만 제거)
  - `ELEVENLABS_API_KEY`, `OPENAI_API_KEY` → **환경에 있어야 함** (skill 들이 사용). `run.sh` 가 시작 시 점검.
  - `_auth.py` 는 `ANTHROPIC_API_KEY` 만 pop 하므로 다른 키는 보존됨 (확인 완료).
- **말할 포인트**:
  - "skill 222개 중 3개만 활성화 — 활성화는 SDK 가, 실제 행동 순서는 system_prompt 가 제어"
  - (마무리) "발표하는 동안 유튜브 영상 1개가 한국어 인포그래픽이 됐습니다."
- **주의**: 이 데모만 외부 키(ElevenLabs/OpenAI) 필요. 나머지 둘은 Claude OAuth 만으로 충분.

**플랜 B (가장 중요)**: 라이브에서 가장 실패 위험 높음(외부 API 2개 의존, 4분 소요).
- **반드시 발표 전날 한 번 완주**시켜 `output/infographic.png` 를 확보해 둔다.
- 라이브 백그라운드가 실패해도 마무리에 **사전 생성한 PNG** 를 열어 보여주면 됨.
- 참고: oauth_version 실측 시 STEP1~3 성공, STEP4 는 OpenAI 키/패키지 부재로 정체된 이력 있음
  (RESULTS.md §4). 이번 데모 환경엔 `OPENAI_API_KEY`/`ELEVENLABS_API_KEY` 가 SET 되어 있음 확인.

---

## 사전 점검 체크리스트 (발표 전날 / 직전)

```bash
cd demo

# 1) OAuth 토큰 유효성 (가장 싸고 빠른 검증 — 데모②의 SDK)
cd 2_cli_vs_sdk && env -u ANTHROPIC_API_KEY \
  /Users/joon/Desktop/10_프로젝트/날짜별/2026/20260529_claude-adk-sdk-tutorial/venv/bin/python3 run_sdk.py
# → "apiKeySource = 'none'" + EXIT 0 이면 토큰 OK
cd ..

# 2) venv 존재
ls /Users/joon/Desktop/10_프로젝트/날짜별/2026/20260529_claude-adk-sdk-tutorial/venv/bin/python3

# 3) 포트 8765 비어있는지 (데모①)
lsof -nP -iTCP:8765 -sTCP:LISTEN || echo "8765 비어있음 OK"

# 4) 외부 키 (데모③ 전용) — SET 떠야 함
env | grep -E "ELEVENLABS_API_KEY|OPENAI_API_KEY" | sed 's/=.*/=SET/'

# 5) 데모③ 입력 mp3 존재
ls -la "/Users/joon/Desktop/10_프로젝트/날짜별/2026/20260529_claude-adk-sdk-tutorial/phase4_harness_in_sdk/yt_downloads/코덱스 18가지 필수 기능 12분 정리.mp3"

# 6) (권장) 데모③ 사전 완주해 output/infographic.png 확보
cd 3_infographic && ./run.sh && tail -f run.log   # 완료 후 output/ 확인
```

체크 항목:
- [ ] OAuth 토큰 유효 (`apiKeySource='none'` 확인)
- [ ] venv python3 실행 가능
- [ ] 포트 8765 비어있음
- [ ] `ELEVENLABS_API_KEY` / `OPENAI_API_KEY` SET (데모③)
- [ ] 입력 mp3 존재
- [ ] 데모③ 사전 완주 → `output/infographic.png` 백업 확보 (플랜 B)
- [ ] 발표 노트북 네트워크 정상 (WebSearch/WebFetch 필요)

---

## 폴더 구조

```
demo/
├── DEMO_GUIDE.md            ← 이 파일
├── _auth.py                 ← OAuth 부트스트랩 (3 데모 공유)
├── .env                     ← CLAUDE_CODE_OAUTH_TOKEN (권한 600)
├── 1_research_webapp/
│   ├── backend.py           ← 원본 본문 그대로 (FastAPI + SSE)
│   ├── frontend.html        ← 신문 스타일 프론트
│   ├── _server.py           ← 데모용 런처 (가드 우회)
│   └── run.sh               ← 포트 8765 기동
├── 2_cli_vs_sdk/
│   ├── prompt.txt           ← 공통 프롬프트
│   ├── fibonacci.py         ← off-by-one 버그 든 대상 코드
│   ├── run_cli.sh           ← claude -p (구독)
│   ├── run_sdk.py           ← ClaudeSDKClient (OAuth, apiKeySource 출력)
│   └── run_both.sh          ← CLI → SDK 순차 비교
└── 3_infographic/
    ├── example8_infographic_pipeline.py   ← WORKDIR=output/, mp3=원본경로
    ├── run.sh               ← 백그라운드 실행 (run.log)
    └── output/              ← 산출물 (infographic.png 최종)
```
