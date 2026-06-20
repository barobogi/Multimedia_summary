# Multimedia Summary App - 지속 개발 문서

**작성일**: 2026-06-20  
**Phase**: 2차 — Railway 배포 완료, 통합 테스트 진행 중  
**상태**: ✅ Railway 배포 성공 · API 정상 응답 확인

---

## ✅ 완료 항목

### Phase 1.1 기본 흐름 (완료)
- [x] FastAPI 백엔드: YouTube → Claude → Daum메일/GitHub/Obsidian 전체 흐름
- [x] Flutter 프론트엔드: 홈/로딩/결과 화면, API 서비스, 로컬 저장소
- [x] Docker 및 Railway 배포 설정 (`config/Dockerfile`, `railway.json`)
- [x] `railway.json` 버그 수정: `DOCKERFILE` 대문자 + `dockerfilePath` 키 수정
- [x] Gmail OAuth → Daum SMTP 교체 (환경변수 단순화)
- [x] **Railway 배포 완료** → `https://multimediasummary-production-55d7.up.railway.app`
- [x] GitHub Pages Multimedia 탭 → `https://barobogi.github.io/Daily_for_Barobogi/information.html`
- [x] 디버깅 로그: `REF/debugging_LOG_Ver_20260620_v0.01.md` (이슈 3개 기록)
- [x] GitHub Pages `information.html` 생성 (`Diary_for_Barobogi` 레포)
- [x] 모든 nav에 Multimedia 탭 추가 (index/logs/ai-study/stats/goals/stock-dashboard)
- [x] `backend/tests/` 테스트 코드: health, summarize (mock)
- [x] `.github/workflows/backend-test.yml` CI 워크플로우
- [x] `docs/DEPLOYMENT.md` Railway 배포 가이드

---

## 🚀 다음 작업 (우선순위 순)

### 1️⃣ Railway 배포 (사용자 직접 진행 필요)

> **`docs/DEPLOYMENT.md` 참조**

핵심 단계:
1. [railway.app](https://railway.app) → New Project → Deploy from GitHub repo
2. repo: `barobogi/260620_3_Multimedia_summary` 선택
3. Environment Variables에 아래 키 입력:

```
ANTHROPIC_API_KEY=sk-ant-...
GITHUB_TOKEN=ghp_...
GMAIL_USER=barobogi79@gmail.com
GMAIL_REFRESH_TOKEN=1//...
GMAIL_CLIENT_ID=...
GMAIL_CLIENT_SECRET=...
```

4. 배포 후 URL 확인: `https://xxx.up.railway.app/docs`
5. `/api/health` 응답 확인

### 2️⃣ Flutter APK 빌드 확인 (사용자 직접)

```bash
cd frontend
flutter pub get          # 의존성 설치
flutter analyze          # 정적 분석
flutter build apk        # APK 빌드
```

`frontend/PLATFORM_SETUP.md` 참조하여 AndroidManifest.xml 설정 확인.

### 3️⃣ 통합 테스트 실행 (Railway 배포 후)

```bash
# 백엔드 로컬 테스트 (API 키 .env 설정 후)
cd backend
pip install -r requirements.txt -r requirements-test.txt
pytest tests/ -v

# 실제 YouTube URL로 end-to-end 테스트
curl -X POST https://xxx.up.railway.app/api/summarize \
  -H "Content-Type: application/json" \
  -d '{"video_url":"https://www.youtube.com/watch?v=VIDEO_ID","platform":"youtube"}'
```

### 4️⃣ Gmail OAuth 설정 (사용자 1회 작업)

Gmail 발송을 위한 OAuth Refresh Token 발급:
1. Google Cloud Console → OAuth 2.0 클라이언트 생성
2. `backend/scripts/get_gmail_token.py` 실행 (아직 없음 - 필요시 작성)
3. 발급된 Refresh Token → Railway 환경변수 `GMAIL_REFRESH_TOKEN`에 입력

---

## 📁 주요 파일 구조

```
260620_3_Multimedia_summary/
├── railway.json                    ✅ Railway 배포 설정 (Dockerfile 빌더)
├── .github/workflows/
│   └── backend-test.yml            ✅ CI: push 시 자동 테스트
├── config/
│   ├── Dockerfile                  ✅ $PORT 환경변수 사용
│   └── Procfile                    (Dockerfile 빌더 사용 시 불필요)
├── backend/
│   ├── main.py                     ✅ FastAPI 앱
│   ├── app/
│   │   ├── config.py               환경변수 로드 (Railway에서 설정)
│   │   ├── models.py               Pydantic 모델
│   │   ├── routes/                 health, summarize 라우터
│   │   └── services/               youtube, claude, gmail, obsidian, github
│   ├── tests/
│   │   ├── conftest.py             ✅ TestClient + mock fixtures
│   │   ├── test_health.py          ✅ health 엔드포인트 3개 테스트
│   │   └── test_summarize.py       ✅ summarize 엔드포인트 3개 테스트
│   ├── requirements.txt            런타임 의존성
│   └── requirements-test.txt       ✅ pytest 의존성
├── frontend/
│   ├── lib/                        Flutter 앱 소스
│   ├── pubspec.yaml                ✅ 불필요한 의존성 제거됨
│   └── assets/                     ✅ images/, icons/, data/, fonts/ 폴더 생성됨
└── docs/
    ├── SETUP.md                    로컬 개발 환경 설정
    └── DEPLOYMENT.md               ✅ Railway 배포 가이드

Diary_for_Barobogi/ (별도 레포)
├── information.html                ✅ Multimedia 탭 (GitHub Pages)
├── index.html                      ✅ nav에 Multimedia 추가됨
├── logs.html                       ✅ nav 업데이트
├── ai-study.html                   ✅ nav 업데이트
├── stats.html                      ✅ nav 업데이트
├── goals.html                      ✅ nav 업데이트
└── stock-dashboard.html            ✅ nav 업데이트
```

---

## ⚠️ 주의사항

1. **.env 파일 절대 커밋 금지** — Railway 환경변수로만 설정
2. `github_service.py`가 모듈 임포트 시 `Github(settings.github_token)` 실행 → 잘못된 토큰이면 앱 시작 시 에러
3. `information.html`은 `https://raw.githubusercontent.com/barobogi/Daily_for_Barobogi/main/_data/multimedia.json`을 fetch — 첫 요약 전까지 빈 화면 표시 (empty state 처리됨)
4. Flutter `assets/fonts/` 에 Pretendard 폰트 파일 없음 → 빌드 전 다운로드 필요 또는 pubspec에서 fonts 섹션 제거

---

## 🔗 관련 링크

- **Barobogi Website**: https://barobogi.github.io/Daily_for_Barobogi/
- **Multimedia 탭**: https://barobogi.github.io/Daily_for_Barobogi/information.html
- **Railway**: https://railway.app
- **GitHub Repo**: https://github.com/barobogi/260620_3_Multimedia_summary (배포 필요)

---

*마지막 업데이트: 2026-06-20*  
*다음 작업: Railway 배포 → Gmail OAuth → Flutter APK 빌드*
