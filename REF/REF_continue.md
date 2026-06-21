# Multimedia Summary App - 지속 개발 문서

**작성일**: 2026-06-20 / **최종 업데이트**: 2026-06-21  
**Phase**: 3차 — 클라이언트 자막 추출 구조 전환 완료  
**상태**: ✅ Render.com 배포 성공 · ✅ 아키텍처 전환 완료 · ⏳ Flutter APK 2차 빌드 완료 대기 → 통합 테스트 예정

---

## ✅ 완료 항목

### Phase 1 — 기본 흐름 구현
- [x] FastAPI 백엔드: YouTube → Claude → Daum메일/GitHub/Obsidian 전체 흐름
- [x] Flutter 프론트엔드: 홈/로딩/결과 화면, API 서비스, 로컬 저장소
- [x] Gmail OAuth → Daum SMTP 교체 (smtp.daum.net:465)

### Phase 2 — Railway 배포 (Railway에서 Render로 이전)
- [x] Railway 배포 완료 → 이후 YouTube IP 차단으로 폐기
- [x] **Render.com으로 이전** → `https://multimedia-summary.onrender.com`
- [x] Health Check 정상: `{"status":"healthy",...}`

### Phase 3 — YouTube IP 차단 우회 (아키텍처 전환)
**문제**: 모든 클라우드 서버(Railway=GCP, Render=AWS계열)에서 YouTube 자막 API 차단

**해결**: 자막 추출을 서버 → Flutter 앱(디바이스)으로 이전

#### 변경된 아키텍처
```
[기존]
Flutter 앱 → (URL 전달) → Render 서버 → YouTube 자막 추출 ← ❌ IP 차단

[변경 후]
Flutter 앱 → YouTube 자막 추출 (디바이스 IP, 차단 없음)
Flutter 앱 → (URL + 자막 전달) → Render 서버 → Claude 요약 → 게시
```

#### 코드 변경 목록
| 파일 | 변경 내용 |
|------|-----------|
| `backend/app/models.py` | `SummaryRequest`에 `transcript: Optional[str]` 추가 |
| `backend/app/routes/summarize_router.py` | transcript 있으면 YouTube 자막 추출 스킵 |
| `backend/app/services/youtube_service.py` | `extract_metadata_only()` 함수 추가 |
| `frontend/pubspec.yaml` | `youtube_explode_dart: ^2.3.0` 추가 |
| `frontend/lib/services/transcript_service.dart` | 신규 — 디바이스에서 자막 추출 |
| `frontend/lib/services/api_service.dart` | transcript 파라미터 추가, URL → Render.com |
| `frontend/lib/screens/home_screen.dart` | 자막 먼저 추출 후 서버 전송 |

### 기타
- [x] YouTube oEmbed API로 메타데이터 추출 (yt-dlp 대체)
- [x] `youtube_transcript_api` 0.6.3 → 1.2.4 업그레이드
- [x] GitHub Pages `information.html` Multimedia 탭 생성
- [x] 루트 `Dockerfile` 추가 (Render.com 배포용)
- [x] `render.yaml` 추가
- [x] 디버깅 로그: `REF/debugging_LOG_Ver_20260620_v0.01.md` (이슈 7개)
- [x] AI Study 탭 포스팅 게시
- [x] Flutter APK 빌드 4단계 오류 해결 (build_runner, DioExceptionType, kotlin.incremental, Gradle lock)
- [x] APK 1차 설치 → "요약생성 실패" 원인 분석 → 자막 실패 처리 + 타임아웃 수정
- [x] ClaudeMonitor.exe 부팅 자동 시작 제거 (레지스트리 HKCU\Run)

---

## 🚀 남은 작업 (우선순위 순)

### 1️⃣ Flutter APK 빌드 및 통합 테스트 ← **진행 중**

**2차 빌드 수정 내역 (2026-06-21)**
- `summary_model.g.dart` 생성 (`build_runner` 실행)
- `DioExceptionType.connectionError` switch 케이스 추가
- `kotlin.incremental=false` (Windows 크로스 드라이브 버그 해결)
- `home_screen.dart`: 자막 추출 실패 시 즉시 에러 표시 (서버 전송 안 함)
- `api_service.dart`: 수신 타임아웃 30초 → 180초

**2차 빌드 완료 후 테스트:**
- 자막 추출 (디바이스 → youtube_explode_dart) 정상 여부
- Claude 요약 (Render 서버) 정상 여부
- Daum 이메일 수신 확인
- GitHub Pages information.html 카드 자동 생성 확인

**빌드 명령어 (참고)**
```powershell
$env:JAVA_HOME = "C:\Program Files\Android\Android Studio\jbr"
cd d:\AI\260620_3_Multimedia_summary\frontend
flutter build apk --release
# APK: build\app\outputs\flutter-apk\app-release.apk (22MB)
# 설치: adb install -r <APK경로>
```

### 2️⃣ AI Study 포스팅 업데이트 (통합 테스트 성공 후)
- "진행중" → 완료 상태로 업데이트
- 최종 구조 다이어그램 추가

---

## 📁 주요 파일 구조

```
260620_3_Multimedia_summary/
├── Dockerfile                      ✅ 루트 Dockerfile (Render.com용)
├── render.yaml                     ✅ Render.com 배포 설정
├── railway.json                    (Railway 폐기, 파일은 유지)
├── .github/workflows/
│   └── backend-test.yml            ✅ CI 워크플로우
├── backend/
│   ├── app/
│   │   ├── config.py               ✅ PROXY_USERNAME/PASSWORD (미사용, 코드만 유지)
│   │   ├── models.py               ✅ SummaryRequest.transcript 추가
│   │   ├── routes/
│   │   │   └── summarize_router.py ✅ transcript 있으면 YouTube 스킵
│   │   └── services/
│   │       ├── youtube_service.py  ✅ oEmbed + extract_metadata_only()
│   │       ├── gmail_service.py    ✅ Daum SMTP
│   │       └── github_service.py   ✅ lazy _gh() 함수
│   └── requirements.txt            ✅ youtube-transcript-api==1.2.4
├── frontend/
│   ├── pubspec.yaml                ✅ youtube_explode_dart 추가
│   └── lib/
│       ├── services/
│       │   ├── transcript_service.dart  ✅ 신규 — 디바이스 자막 추출
│       │   └── api_service.dart         ✅ transcript 파라미터 + Render URL
│       └── screens/
│           └── home_screen.dart         ✅ 자막 먼저 추출 → 서버 전송
└── REF/
    ├── REF_continue.md
    └── debugging_LOG_Ver_20260620_v0.01.md  ✅ 이슈 5개 기록

Diary_for_Barobogi/ (별도 레포)
├── information.html                ✅ Multimedia 탭
└── ai-study.html                   ✅ 개발 포스팅 (20260620-3, 진행중)
```

---

## 🔗 관련 링크

- **Render API**: `https://multimedia-summary.onrender.com`
- **Health Check**: `https://multimedia-summary.onrender.com/api/health`
- **Multimedia 탭**: `https://barobogi.github.io/Daily_for_Barobogi/information.html`
- **GitHub Repo**: `https://github.com/barobogi/Multimedia_summary`
- **Railway (폐기)**: `https://multimediasummary-production-55d7.up.railway.app` (YouTube IP 차단으로 미사용)

---

## ⚠️ 주의사항

1. **.env 파일 절대 커밋 금지** — API 키는 Render 환경변수로만 설정
2. **Render 무료 플랜**: 15분 비활성 시 슬립 → 첫 요청 30~60초 대기 가능
3. Render Environment Variables 현재 설정: ANTHROPIC_API_KEY, GITHUB_TOKEN, DAUM_ID, DAUM_PW
4. `information.html`은 첫 요약 성공 전까지 빈 화면 (정상)
5. `youtube_explode_dart`는 자막 있는 영상만 지원 — 자막 없는 영상은 에러 메시지 표시됨

---

## 🐛 이슈 히스토리 요약

| # | 이슈 | 해결 |
|---|------|------|
| 1 | Railway Dockerfile 경로 오류 | `DOCKERFILE` 대문자 + `dockerfilePath` 키 수정 |
| 2 | Railway 환경변수 미주입 → 앱 크래시 | Optional 처리 + lazy 함수 |
| 3 | Railway Public Domain 미생성 | Settings → Networking에서 직접 생성 |
| 4 | yt-dlp IP 차단 + 라이브러리 버전 문제 | oEmbed 전환 + 1.2.4 업그레이드 |
| 5 | 모든 클라우드 IP YouTube 차단 | 아키텍처 전환: 클라이언트 자막 추출 |
| 6 | Flutter APK 빌드 4단계 오류 | build_runner 실행, DioExceptionType 추가, kotlin.incremental=false, Gradle lock 해제 |
| 7 | APK "요약생성 실패" | 자막 실패 시 즉시 에러 표시 + 타임아웃 180초 |

자세한 내용: `REF/debugging_LOG_Ver_20260620_v0.01.md`

---

*마지막 업데이트: 2026-06-21*  
*다음 작업: 2차 APK 빌드 완료 → 폰 설치 → 통합 테스트 → AI Study 포스팅 완료 처리*
