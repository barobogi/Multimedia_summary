# Multimedia Summary App - 지속 개발 문서

**작성일**: 2026-06-20 / **최종 업데이트**: 2026-06-21  
**Phase**: 4차 — Gemini API 아키텍처 전환 완료  
**상태**: ✅ Render.com 배포 성공 · ✅ Gemini 요약 테스트 성공 · ⏳ APK v1.0 빌드 전

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

### Phase 3 — YouTube IP 차단 우회 시도 (클라이언트 자막 추출 — 최종 실패)
- [x] youtube_explode_dart → XmlParserException (YouTube API 변경)
- [x] timedtext API → 빈 응답
- [x] 수동 쿠키 → 빈 응답
- [x] cookie_jar 자동 세션 → 빈 응답
- [x] 5가지 방법 전부 실패 → **근본 원인: 브라우저 인증 세션 재현 불가**

### Phase 4 — Gemini API 아키텍처 전환 ✅
**문제**: YouTube 자막 추출은 실제 브라우저 없이 불가능

**해결**: Gemini API (Google 계열)는 YouTube 영상 직접 접근 가능 → 자막 추출 불필요

#### 최종 아키텍처
```
[Phase 4 최종]
Flutter 앱 → (YouTube URL만 전달) → Render 서버
Render 서버 → Gemini 2.5 Flash (YouTube 영상 직접 이해 → 텍스트 추출)
Render 서버 → Claude (구조화 요약)
Render 서버 → Daum메일 / GitHub Pages / Obsidian 자동 배포
```

#### 코드 변경 목록
| 파일 | 변경 내용 |
|------|-----------|
| `backend/app/services/gemini_service.py` | 신규 — Gemini YouTube 직접 접근 |
| `backend/app/services/__init__.py` | gemini_service import 추가 |
| `backend/app/routes/summarize_router.py` | YouTube → Gemini 자막 추출 연동 |
| `backend/requirements.txt` | `google-generativeai==0.8.3` 추가 |
| `frontend/pubspec.yaml` | cookie_jar, dio_cookie_manager 제거 |
| `frontend/lib/services/api_service.dart` | transcript 파라미터 제거 |
| `frontend/lib/screens/home_screen.dart` | TranscriptService 제거, URL만 전송 |
| `frontend/lib/services/transcript_service.dart` | **삭제** |
| `.gitignore` | `/lib/` 수정 (frontend/lib 누락 해결) |

#### 테스트 결과
```
POST /api/gemini-test
영상: https://youtu.be/eImK97E4w20 (레트로 게임 앱 소개)
결과: ✅ 성공 — gemini-2.5-flash로 한국어 완벽 요약 (약 2000자)
```

### 기타
- [x] YouTube oEmbed API로 메타데이터 추출
- [x] GitHub Pages `information.html` Multimedia 탭 생성
- [x] Render.com 배포 + GEMINI_API_KEY 환경변수 설정
- [x] 디버깅 로그: 이슈 #11까지 기록 완료
- [x] .gitignore 수정으로 frontend/lib/ Dart 소스 첫 커밋 완료
- [x] Windows Downloads 폴더 → D:\Downloads 심볼릭 링크 이전
- [x] AI Study 탭 포스팅: "Barobogi 데스크탑 최적화 도전 #1"

---

## 🚀 남은 작업 (우선순위 순)

### 1️⃣ 통합 테스트 (Render 재배포 후)
- Render 재배포 대기 (Gemini service 신규 코드 반영)
- `POST /api/summarize` 전체 플로우 테스트
- Claude 요약 → Daum 이메일 수신 확인
- GitHub Pages information.html 카드 생성 확인

### 2️⃣ APK v1.0 빌드
- 앱 아이콘 교체 (flutter_launcher_icons 또는 직접 교체)
- `pubspec.yaml` 버전 확인 (현재 `1.0.0+1`)
- `flutter build apk --release`
- `adb install -r` 폰 설치
- 실기기 통합 테스트

### 3️⃣ 마무리
- CHANGELOG.md 작성 (v1.0 소급 포함)
- AI Study 포스팅 완료 상태로 업데이트
- REF_continue.md 최종화

---

## 📁 주요 파일 구조

```
260620_3_Multimedia_summary/
├── Dockerfile                      ✅ 루트 Dockerfile (Render.com용)
├── render.yaml                     ✅ Render.com 배포 설정
├── backend/
│   ├── app/
│   │   ├── models.py               ✅ SummaryRequest
│   │   ├── routes/
│   │   │   └── summarize_router.py ✅ Gemini 연동
│   │   └── services/
│   │       ├── gemini_service.py   ✅ 신규 — YouTube 직접 접근
│   │       ├── youtube_service.py  ✅ oEmbed 메타데이터
│   │       ├── claude_service.py   ✅ 구조화 요약
│   │       ├── gmail_service.py    ✅ Daum SMTP
│   │       └── github_service.py   ✅ GitHub Pages
│   └── requirements.txt            ✅ google-generativeai==0.8.3
├── frontend/
│   ├── pubspec.yaml                ✅ cookie_jar 제거
│   └── lib/
│       ├── services/
│       │   ├── api_service.dart    ✅ URL만 전송
│       │   └── clipboard_helper.dart
│       └── screens/
│           └── home_screen.dart    ✅ TranscriptService 제거
└── REF/
    ├── REF_continue.md             ✅ (이 파일)
    └── debugging_LOG_Ver_20260620_v0.01.md  ✅ 이슈 #11까지

Diary_for_Barobogi/ (별도 레포)
├── information.html                ✅ Multimedia 탭
└── ai-study.html                   ✅ "데스크탑 최적화 도전 #1" 포스팅
```

---

## 🔗 관련 링크

- **Render API**: `https://multimedia-summary.onrender.com`
- **Health Check**: `https://multimedia-summary.onrender.com/api/health`
- **Gemini Test**: `POST https://multimedia-summary.onrender.com/api/gemini-test`
- **Multimedia 탭**: `https://barobogi.github.io/Daily_for_Barobogi/information.html`
- **GitHub Repo**: `https://github.com/barobogi/Multimedia_summary`

---

## ⚠️ 주의사항

1. **.env 파일 절대 커밋 금지** — API 키는 Render 환경변수로만 설정
2. **Render 무료 플랜**: 15분 비활성 시 슬립 → 첫 요청 30~60초 대기 가능
3. Render Environment Variables: `ANTHROPIC_API_KEY`, `GITHUB_TOKEN`, `DAUM_ID`, `DAUM_PW`, `GEMINI_API_KEY`
4. Gemini API: `gemini-2.5-flash` 모델 사용 (prefix: `models/gemini-2.5-flash`)
5. Samsung Secure Folder = 별도 사용자(user 150) → APK 설치 시 보안 폴더에는 설치 금지

---

## 🐛 이슈 히스토리 요약

| # | 이슈 | 해결 |
|---|------|------|
| 1 | Railway Dockerfile 경로 오류 | `dockerfilePath` 키 수정 |
| 2 | Railway 환경변수 미주입 → 앱 크래시 | Optional 처리 + lazy 함수 |
| 3 | Railway Public Domain 미생성 | Settings → Networking에서 직접 생성 |
| 4 | yt-dlp IP 차단 + 라이브러리 버전 문제 | oEmbed 전환 + 1.2.4 업그레이드 |
| 5 | 모든 클라우드 IP YouTube 차단 | → Phase 3 클라이언트 자막 추출 시도 |
| 6 | Flutter APK 빌드 4단계 오류 | build_runner, DioExceptionType, kotlin.incremental=false |
| 7 | APK "요약생성 실패" | 자막 실패 시 즉시 에러 표시 + 타임아웃 180초 |
| 8 | youtu.be URL 파싱 실패 + SnackBar 3초 문제 | _extractVideoId() + AlertDialog 전환 |
| 9 | AndroidManifest INTERNET 권한 누락 | `<uses-permission android:name="android.permission.INTERNET" />` 추가 |
| 10 | youtube_explode_dart XmlParserException | 라이브러리 제거 + 직접 Dio 구현 |
| 11 | YouTube 자막 5가지 방법 전부 실패 | **Gemini API 아키텍처 전환** (근본 해결) |

자세한 내용: `REF/debugging_LOG_Ver_20260620_v0.01.md`

---

*마지막 업데이트: 2026-06-21*  
*다음 작업: 통합 테스트 → APK v1.0 빌드 (아이콘 포함) → CHANGELOG.md 작성*
