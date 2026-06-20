# Multimedia Summary App - 지속 개발 문서

**작성일**: 2026-06-20  
**Phase**: 2차 — Railway 배포 완료, YouTube IP 차단 이슈 해결 진행 중  
**상태**: ✅ Railway 배포 성공 · ⏳ Webshare 프록시 설정 대기 중

---

## ✅ 완료 항목

### Phase 1 — 기본 흐름 구현
- [x] FastAPI 백엔드: YouTube → Claude → Daum메일/GitHub/Obsidian 전체 흐름
- [x] Flutter 프론트엔드: 홈/로딩/결과 화면, API 서비스, 로컬 저장소
- [x] Docker 및 Railway 배포 설정 (`config/Dockerfile`, `railway.json`)
- [x] Gmail OAuth → Daum SMTP 교체 (smtp.daum.net:465, 환경변수: DAUM_ID/DAUM_PW)

### Phase 2 — Railway 배포
- [x] `railway.json` 버그 수정: `DOCKERFILE` 대문자 + `dockerfilePath` 키
- [x] `config.py` Optional 처리: anthropic_api_key, github_token → 시작 크래시 방지
- [x] `github_service.py` lazy `_gh()` 함수: 모듈 로드 시 즉시 실행 방지
- [x] **Railway 배포 완료** → `https://multimediasummary-production-55d7.up.railway.app`
- [x] Railway Public Domain 생성 (Settings → Networking → Generate Domain → port 8000)
- [x] `/api/health` 정상 응답 확인

### Phase 3 — YouTube 자막 추출 이슈 대응
- [x] yt-dlp → **YouTube oEmbed API**로 메타데이터 추출 교체 (클라우드 IP 무관)
- [x] `youtube_transcript_api` 0.6.3 → **1.2.4 업그레이드** (InnerTube API 방식)
- [x] Webshare 프록시 코드 추가 (`youtube_service.py` + `config.py`)
  - PROXY_USERNAME / PROXY_PASSWORD 환경변수 지원
  - 미설정 시 직접 연결로 fallback

### 기타
- [x] GitHub Pages `information.html` 생성 (`Diary_for_Barobogi` 레포)
- [x] 전체 nav에 Multimedia 탭 추가 (index/logs/ai-study/stats/goals/stock-dashboard)
- [x] `backend/tests/` 테스트 코드: health, summarize (mock)
- [x] `.github/workflows/backend-test.yml` CI 워크플로우
- [x] 디버깅 로그: `REF/debugging_LOG_Ver_20260620_v0.01.md` (이슈 4개 기록)
- [x] AI Study 탭 포스팅: "동영상 요약 및 자동 게시 앱 개발 _ 진행중"

---

## 🚧 현재 블로커

### YouTube IP 차단 (Railway → YouTube 차단)
Railway 서버(Google Cloud IP)가 YouTube에 차단되어 자막 추출 불가.  
코드는 완료. **Webshare 프록시 설정만 남음.**

**다음 진행 순서:**
1. [webshare.io](https://webshare.io) 무료 가입
2. Dashboard → Proxy → Residential → Proxy Username/Password 복사
3. Railway Variables 추가:
   ```
   PROXY_USERNAME = (webshare username)
   PROXY_PASSWORD = (webshare password)
   ```
4. Railway 재배포 후 테스트:
   ```
   영상 URL: https://youtu.be/x1b2AdDmLhw
   ```

---

## 🚀 남은 작업 (우선순위 순)

### 1️⃣ Webshare 프록시 설정 (위 블로커 해결)

### 2️⃣ 통합 테스트 (Webshare 완료 후)
- 실제 YouTube 영상 → 요약 → Daum 이메일 수신 확인
- GitHub Pages `information.html` 카드 자동 생성 확인
- 전체 플로우 end-to-end 검증

### 3️⃣ Flutter APK 빌드 및 테스트
```bash
cd frontend
flutter pub get
flutter analyze
flutter build apk
```
- Railway API URL 연동 확인
- Android 기기 설치 테스트
- `frontend/PLATFORM_SETUP.md` 참조

### 4️⃣ AI Study 포스팅 업데이트 (앱 완성 후)
- "진행중" → 완료 상태로 업데이트
- 최종 결과 스크린샷 추가

---

## 📁 주요 파일 구조

```
260620_3_Multimedia_summary/
├── railway.json                    ✅ Railway 배포 설정
├── .github/workflows/
│   └── backend-test.yml            ✅ CI: push 시 자동 테스트
├── config/
│   └── Dockerfile                  ✅ $PORT 환경변수 사용
├── backend/
│   ├── app/
│   │   ├── config.py               ✅ PROXY_USERNAME/PASSWORD 추가됨
│   │   ├── services/
│   │   │   ├── youtube_service.py  ✅ oEmbed + 1.2.4 + Webshare 프록시
│   │   │   ├── gmail_service.py    ✅ Daum SMTP
│   │   │   └── github_service.py   ✅ lazy _gh() 함수
│   ├── tests/                      ✅ pytest mock 테스트
│   └── requirements.txt            ✅ youtube-transcript-api==1.2.4
├── frontend/                       Flutter 앱
└── REF/
    ├── REF_continue.md             ← 이 파일
    └── debugging_LOG_Ver_20260620_v0.01.md  ✅ 이슈 4개 기록

Diary_for_Barobogi/ (별도 레포)
├── information.html                ✅ Multimedia 탭
└── ai-study.html                   ✅ 개발 포스팅 추가됨 (20260620-3)
```

---

## 🔗 관련 링크

- **Railway API**: `https://multimediasummary-production-55d7.up.railway.app`
- **Health Check**: `https://multimediasummary-production-55d7.up.railway.app/api/health`
- **Multimedia 탭**: `https://barobogi.github.io/Daily_for_Barobogi/information.html`
- **AI Study 포스팅**: `https://barobogi.github.io/Daily_for_Barobogi/ai-study.html`
- **GitHub Repo**: `https://github.com/barobogi/260620_3_Multimedia_summary`

---

## ⚠️ 주의사항

1. **.env 파일 절대 커밋 금지** — API 키는 Railway 환경변수로만 설정
2. Railway Variables 현재 설정값: ANTHROPIC_API_KEY, GITHUB_TOKEN, DAUM_ID, DAUM_PW, PORT=8000
3. `information.html`은 `_data/multimedia.json`을 fetch — 첫 요약 성공 전까지 빈 화면

---

*마지막 업데이트: 2026-06-20*  
*다음 작업: Webshare 프록시 설정 → 통합 테스트 → Flutter APK 빌드*
