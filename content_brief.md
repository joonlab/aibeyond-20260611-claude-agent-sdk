# ai&beyond 발표 콘텐츠 브리프 — Claude Agent SDK

> 팀 공유용 단일 소스. 발표 덱·튜토리얼 repo README·데모 가이드 모두 이 문서를 기준으로 작성한다.

## 0. 발표 메타

- **발표 제목**: Claude Agent SDK로 어떤 것까지 가능할까? (Claude Code CLI 완전 대체 가능?!)
- **행사**: CMDSPACE 「AI & Beyond」 — AI 전문가 프리미엄 멤버십, 멤버 인사이트 발표
- **일시**: 2026-06-11 (목) 20:00–22:00 중 발표 슬롯
- **발표자**: 박준 (JoonLab) — 자기소개 장표 불필요
- **분량**: 15~20분 라이트닝 → 슬라이드 15장 내외
- **라이브 데모 3종**: ① Research 웹앱 ② CLI vs SDK 나란히 비교 ③ 3-Skill 인포그래픽 파이프라인 (모두 OAuth/구독 기반)

## 1. 여정 (스토리라인)

1. **출발점**: 유튜브 영상 "직접 클로드 만들어봤어 (생각보다 쉬움)" 시청
   - 영상 자체도 Claude로 처리: youtube-download skill로 mp3 추출 → elevenlabs-stt로 전사 → 요약
   - 핵심 메시지: "바닥부터 만들지 말고 Claude Code harness를 상속하라"
2. **4-Phase 튜토리얼**을 Claude Code와의 대화만으로 구축 (작업폴더: `20260529_claude-adk-sdk-tutorial`)
3. **과금 정책 이슈** 발견 (커뮤니티 질문) → 공식 문서 직접 검증
4. **OAuth 포팅 실측** → 20개 스크립트 전부 구독 토큰만으로 동작 확인
5. **배포 옵션 5종** 정리 (Docker/Cloudflare/AWS Fargate/AgentCore/Vercel Sandbox)

## 2. 4-Phase 튜토리얼 요약 (실측 데이터 포함)

### Phase 1 — SDK 기초 6예제
| # | 예제 | 핵심 |
|---|---|---|
| 1 | `query()` 5줄 에이전트 | one-shot. 캐시 효과: 1차 $0.374 → 2차 $0.170 (55% 절감) |
| 2 | `ClaudeSDKClient` 멀티턴 | "타이 음식" 기억 테스트 — 메모리 자동 유지 |
| 3 | 권한 콜백 `can_use_tool` | `rm -rf` 차단. **함정**: `allowed_tools`에 넣으면 콜백 우회, `setting_sources=[]` 필수 |
| 4 | `@tool` + `create_sdk_mcp_server` | in-process MCP 도구 3종(날씨/계산/DB). SDK가 자율 병렬 호출 |
| 5 | system_prompt 3모드 | 기본(stripped) vs claude_code preset vs 커스텀 페르소나 |
| 6 | Research Agent 통합 | 도구+페르소나+멀티턴. "확인 불가" 마커 준수. Opus 계획+Haiku 실행 하이브리드 → 88% 비용 절감 제안 |

### Phase 2 — Claude Code CLI 일상 작업을 SDK로 재현 (4종)
| # | 시나리오 | 결과 |
|---|---|---|
| 1 | 코드베이스 탐색 | Glob+Read로 파일별 요약+학습 순서 추천 |
| 2 | git diff → PR description | Summary/Changes/Test plan 자동 생성 |
| 3 | 다중 파일 일괄 리팩토링 | dry-run→apply→grep 검증. **발견**: `async with` 블록별 세션 독립 → 멀티턴은 같은 client 안에서 |
| 4 | 구조화 코드 리뷰 | JSON 출력 → `json.loads()` 파싱 → 자동화 파이프라인 연결 |

### Phase 3 — Research 웹앱 (FastAPI + SSE)
- ClaudeSDKClient를 FastAPI 백엔드에 임베드, SSE 5종 이벤트(status/thinking/tool/chunk/done)로 실시간 스트리밍
- 신문 스타일 프론트엔드("The Research Daily")
- 실측: 질문 1건 = 43.5초 / $0.251 / 5턴 (WebSearch 1 + WebFetch 3)

### Phase 4 — Claude Code Harness를 SDK로 정밀 구현 (8예제)
공식 문서(code.claude.com/docs/en/agent-sdk/*)를 cmux browser + 5개 병렬 sub-agent로 조사 후 전부 실증.

| Harness | CLI | SDK | 판정 |
|---|---|---|---|
| Skills | `~/.claude/skills/SKILL.md` | `setting_sources=["user"]` + `skills=[...]` 필터 | ✅ 완전 호환 |
| Hooks | settings.json 셸 명령 | `hooks={"PreToolUse":[HookMatcher(...)]}` async 콜백 | ✅ 함수형으로 진화 |
| Subagents | `.claude/agents/*.md` | `agents={"name": AgentDefinition(...)}` | ✅ 병렬 spawn + 모델 차등 |
| Slash Commands | `~/.claude/commands/*.md` | 파일 그대로 자동 인식, prompt에 "/cmd" | ✅ (register API는 없음) |
| Plugins | `/plugin install` | `plugins=[{"type":"local","path":...}]` | 🔶 local만 |
| Sessions | `--continue/--resume` | `resume=sid` / `fork_session=True` | ✅ fork까지 |
| SessionStorage | `~/.claude/projects/` 자동 | `session_store=` 커스텀(Redis/S3 등) dual-write | ✅ SDK가 더 강력 |
| MCP | `.mcp.json` | `mcp_servers={...}` in-process+remote | ✅ |
| SessionStart/End hook | settings.json | **Python SDK 직접 불가** (TS는 가능) → settings.json 우회 | ⚠️ 부분 |

핵심 실증:
- **Ex2 Hooks**: `.env` 쓰기 deny — `permissionDecision: "deny"` 동작
- **Ex3 Subagents**: code-reviewer + test-analyzer + docs-writer 3개 동시 spawn (40.4s/$0.358, Haiku 위임)
- **Ex5 Sessions**: resume="박준" 기억 / fork="준이" 분기 / 원본 무영향 — 5단계 검증
- **Ex7 youtube-download skill**: 222개 skill 중 1개만 활성화해 발동. **발견: Skill 도구 ≠ Skill 동작** — 활성화는 SDK가, 실제 행동은 system_prompt가 제어
- **Ex8 3-Skill 파이프라인**: youtube-download → elevenlabs-stt → openai-gpt-image-2 단일 prompt로 4단계 자율 진행 → "코덱스 18가지 필수 기능" 한국어 인포그래픽 PNG (230.8s/$0.72/16턴)

## 3. 과금 정책 (태극님 질문 답변) — 핵심 장표

> 질문 원문(2026-06-04): "아 근데 준님, Claude Agent SDK 토큰 사용량이 이제 구독제에서 제외된다고 봤던 것 같은데요. 맞나요?"

### 질문 ① API Key 없이 Agent SDK 사용 가능? → ✅ 가능 (지금도 유효)
- Agent SDK는 API 직접 호출이 아니라 **Claude Code CLI를 subprocess로 실행** → CLI의 OAuth 토큰(`claude setup-token`, `sk-ant-oat01-...`) 사용
- `[클라이언트] → [Agent SDK] → [Claude Code CLI] → [Claude]`
- 출처: velog 조현상 "API Key 없이 Claude Agent 서버 만들기! #1" (2026-04-02)

### 질문 ② 구독제에서 토큰 사용량 제외? → ✅ 맞음 (**2026-06-15부터** — 발표일 기준 4일 후!)
- 공식: "Starting June 15, 2026, Claude Agent SDK and `claude -p` usage no longer counts toward your Claude plan's usage limits."
- 구독 한도는 인터랙티브 전용으로 보존, Agent SDK는 **플랜별 월간 크레딧**으로 분리:

| 플랜 | 월간 Agent SDK 크레딧 |
|---|---|
| Pro | $20 |
| Max 5x | $100 |
| Max 20x | $200 |
| Team Standard / Premium | $20 / $100 per seat |
| Enterprise | $20 (usage) / $200 (Premium seat) |

- 작동: 1회 opt-in → 매월 리셋(이월 없음) → Agent SDK 사용 시 크레딧 먼저 차감(drains first) → 소진 시 usage credits(종량제) 또는 중단
- 크레딧 적용: Agent SDK, `claude -p`, GitHub Actions, 서드파티 구독 인증 앱
- 미적용(기존 구독 한도 그대로): 인터랙티브 Claude Code, 웹/데스크톱/모바일 Claude, Claude Cowork
- 시점 변화: velog(4월) "구독 한도 그대로 적용" → 6/15부로 outdated. **"구독으로 무제한" 표현은 이제 틀림**
- 출처: https://support.claude.com/en/articles/15036540-use-the-claude-agent-sdk-with-your-claude-plan

### OAuth 실측 증명 (oauth_version/RESULTS.md)
- 20개 스크립트를 `ANTHROPIC_API_KEY` 강제 제거 + `CLAUDE_CODE_OAUTH_TOKEN`만으로 전부 재실행
- init 로그 `apiKeySource`: `'ANTHROPIC_API_KEY'` → **`'none'`** 으로 바뀜 = 종량제 경로 아님
- 인증 실패(is_error=True) 0건

### 실무 시사점
- 개인 실험/자동화 → 크레딧 범위($20~$200) 내 충분, OAuth 방식 유효
- 프로덕션/대규모 → 공식 문서가 **API Key 종량제 명시 권장**. 크레딧은 개인 단위(풀링 불가)
- 공개 백엔드에 OAuth 토큰 박는 것 금지(ToS·rate limit) → OAuth는 로컬/개인용

## 4. 팩트체크 결론 — "Claude Code CLI 완전 대체 가능?!"

**거의 YES, 단 목적이 다르다.**
- CLI에서 가능한 harness(Skills/Hooks/Subagents/Commands/MCP/Sessions)는 사실상 전부 SDK로 구현 가능 — Phase 4에서 전부 실증
- 예외 2가지: ① Python SDK에서 SessionStart/End hook 직접 정의 불가(TS는 가능, settings.json 우회 가능) ② 인터랙티브 터미널 UX 자체
- SDK가 더 강한 것: 런타임 동적 정의(subagent/hook), 함수형 hook(LLM-as-judge 가능), 커스텀 SessionStore(Redis/S3), `setting_sources` 격리, 제품 임베드
- 한 줄 정리: **"Claude Code = SDK + 표준 harness 번들"**. CLI로 프로토타입 → SDK로 프로덕션이 정석 워크플로우
- 단 6/15 이후 과금 관점: 인터랙티브(CLI)는 구독 한도, SDK는 월간 크레딧 — **"완전 대체"하면 과금 버킷이 바뀐다**는 게 새 변수

## 5. 주요 트러블슈팅 (발표에서 1~2개 언급용)

1. `can_use_tool` 콜백 미발화 → `allowed_tools` 자동 승인 + 사용자 settings 상속이 원인, `setting_sources=[]`로 해결
2. 첫 호출 $0.37 → 사용자 환경 시스템 프롬프트 58K 토큰 캐시 생성 비용. 2회차부터 캐시 히트
3. `async with` 블록 간 컨텍스트 미공유 → 같은 client 안에서 멀티턴
4. SessionKey가 Python에서 dict로 전달 (문서는 TS 객체 표기) — 방어적 helper 필요

## 6. 산출물 링크 (덱 마지막 장표용 — 실제 URL은 배포 후 lead가 채움)

- 발표 덱: `https://aibeyond-20260611-claude-agent-sdk.vercel.app` (예정)
- 튜토리얼 repo: `https://github.com/joonlab/claude-agent-sdk-tutorial` (예정)
- 참고: 영상 https://youtu.be/2tF77s2IOC0 / velog 글 / 공식 Help Center 문서

## 7. 데모 시연 전략 (15~20분 발표 내 배치)

- **발표 시작 직후**: ③ 인포그래픽 파이프라인을 백그라운드로 실행해 둠 (약 4분 소요 → 발표 중반에 결과 확인)
- **중반**: ② CLI vs SDK 나란히 비교 (같은 프롬프트, 같은 결과, apiKeySource 차이 강조) — 1~2분
- **중후반**: ① Research 웹앱 라이브 (질문 입력 → SSE 스트리밍 → 보고서) — 1~2분
- **마무리 직전**: ③ 결과 인포그래픽 PNG 오픈 → "발표하는 동안 영상 1개가 인포그래픽이 됐습니다"
