# 배포 및 실행 체크리스트

**목표**: Multimedia Summary App을 Railway에 배포하고 실제로 작동하는지 확인하기

---

## ✅ 체크리스트 (순서대로 진행)

### Phase 1: Railway 배포 (필수)

- [ ] **1.1 Railway 계정 생성**
  - https://railway.app 방문
  - GitHub 계정으로 가입/로그인

- [ ] **1.2 GitHub 리포지토리 연결**
  - Railway Dashboard → "New Project"
  - "Deploy from GitHub" 선택
  - 리포지토리: `barobogi/260620_3_Multimedia_summary` 선택
  - Deploy 클릭

- [ ] **1.3 환경 변수 설정**
  - Railway Dashboard → Variables 탭
  - 다음 6개 변수 입력:
    ```
    ANTHROPIC_API_KEY = sk-ant-v1-xxxxx...
    GITHUB_TOKEN = ghp_xxxxx...
    GITHUB_REPO = barobogi/Daily_for_Barobogi
    GITHUB_USERNAME = barobogi
    GMAIL_USER = barobogi79@gmail.com
    GMAIL_REFRESH_TOKEN = 1//0xxxxx...
    GMAIL_CLIENT_ID = xxxxx...
    GMAIL_CLIENT_SECRET = xxxxx...
    ```
  - 각 값은 [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) 의 "환경 변수 가져오기" 참조

- [ ] **1.4 배포 확인**
  - Railway Dashboard → Deployments 탭
  - 최신 배포가 "Success" 상태인지 확인
  - Logs에서 에러 없는지 확인
  ```
  2026-06-20 12:00:00 🚀 Multimedia Summary API starting...
  2026-06-20 12:00:01 Uvicorn running on http://0.0.0.0:8000
  ```

- [ ] **1.5 API 헬스 체크**
  ```bash
  # Railway 배포 URL 확인 (Settings → Public Domain)
  curl https://YOUR-APP.up.railway.app/api/health
  
  # 응답 예상:
  # {"status":"healthy","timestamp":"2026-06-20T12:00:00","service":"Multimedia Summary API"}
  ```

---

### Phase 2: Gmail OAuth 설정 (필수)

> 메일 발송 기능이 필요할 때

- [ ] **2.1 Google Cloud Console 접속**
  - https://console.cloud.google.com 방문
  - 새 프로젝트 생성: `multimedia-summary`

- [ ] **2.2 Gmail API 활성화**
  - "API 및 서비스" → "라이브러리"
  - "Gmail API" 검색 → 활성화

- [ ] **2.3 OAuth 2.0 클라이언트 생성**
  - "API 및 서비스" → "사용자 인증 정보"
  - "사용자 인증 정보 만들기" → "OAuth 클라이언트 ID"
  - 응용 프로그램 유형: "데스크톱"
  - `credentials.json` 다운로드

- [ ] **2.4 Refresh Token 발급**
  - 아래 Python 스크립트 실행 (별도 지원 필요하면 요청):
  ```python
  from google_auth_oauthlib.flow import InstalledAppFlow
  SCOPES = ['https://www.googleapis.com/auth/gmail.send']
  flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
  creds = flow.run_local_server(port=0)
  print("Refresh Token:", creds.refresh_token)
  ```
  - 발급된 Refresh Token을 Railway `GMAIL_REFRESH_TOKEN` 변수에 입력

- [ ] **2.5 메일 전송 테스트**
  ```bash
  curl -X POST https://YOUR-APP.up.railway.app/api/summarize \
    -H "Content-Type: application/json" \
    -d '{
      "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
      "platform": "youtube"
    }'
  
  # barobogi79@gmail.com으로 메일 수신 확인
  ```

---

### Phase 3: GitHub Pages 업데이트 (필수)

> `Diary_for_Barobogi` 리포지토리 업데이트

- [ ] **3.1 changes 커밋**
  ```bash
  cd /path/to/Diary_for_Barobogi
  git add information.html index.html logs.html ai-study.html stats.html goals.html stock-dashboard.html
  git commit -m "Add Multimedia tab and information.html"
  git push origin main
  ```

- [ ] **3.2 GitHub Pages 반영 확인**
  - https://barobogi.github.io/Daily_for_Barobogi/information.html 방문
  - Multimedia 탭이 나타났는지 확인
  - (처음에는 데이터 없음 → 첫 요약 후 표시됨)

---

### Phase 4: Flutter APK 빌드 (선택)

> 모바일 앱으로 사용하려면

- [ ] **4.1 Flutter SDK 설치 확인**
  ```bash
  flutter doctor
  # 모든 항목이 ✓ 표시되는지 확인
  ```

- [ ] **4.2 의존성 설치**
  ```bash
  cd frontend
  flutter pub get
  ```

- [ ] **4.3 Pretendard 폰트 처리**
  - **옵션 A (권장)**: pubspec.yaml에서 fonts 섹션 제거
    ```yaml
    # 제거:
    fonts:
      - family: Pretendard
        fonts:
          - asset: assets/fonts/...
    ```
  - **옵션 B**: 폰트 파일 다운로드 후 `assets/fonts/`에 추가
    - https://releases.github.com/notofonts/NotoSansKR/v1.006/NotoSansKR-Regular.otf

- [ ] **4.4 Android APK 빌드**
  ```bash
  flutter build apk --release
  # 생성 위치: build/app/outputs/apk/release/app-release.apk
  ```

- [ ] **4.5 APK 설치 (실기기)**
  ```bash
  adb install build/app/outputs/apk/release/app-release.apk
  ```

- [ ] **4.6 앱 테스트**
  - YouTube 영상 URL 공유 → Multimedia Summary 앱 선택
  - 요약 생성 확인

---

### Phase 5: 통합 테스트 (선택)

> 전체 시스템이 정상 작동하는지 확인

- [ ] **5.1 백엔드 로컬 테스트**
  ```bash
  cd backend
  pip install -r requirements.txt -r requirements-test.txt
  pytest tests/ -v
  
  # 예상 결과:
  # test_health.py::test_health_ok PASSED
  # test_summarize.py::test_summarize_invalid_url PASSED
  # ... (모두 PASSED)
  ```

- [ ] **5.2 실제 YouTube URL로 E2E 테스트**
  ```bash
  curl -X POST https://YOUR-APP.up.railway.app/api/summarize \
    -H "Content-Type: application/json" \
    -d '{
      "video_url": "https://www.youtube.com/watch?v=ACTUAL_VIDEO_ID",
      "platform": "youtube",
      "language": "ko"
    }'
  
  # 응답에 summary, key_insights, categories 포함되어야 함
  ```

- [ ] **5.3 배포된 데이터 확인**
  - Gmail: barobogi79@gmail.com 메일 수신 확인
  - Obsidian: `Multimedia/{YYYY}/{MM}/{DD}/` 폴더에 .md 파일 생성 확인
  - GitHub Pages: https://barobogi.github.io/Daily_for_Barobogi/information.html에 카드 표시 확인

---

## 🆘 문제 해결

### Railway 배포 실패

**에러**: `Dockerfile not found`
- ✅ 해결: `railway.json` 확인 → `dockerfile: "./config/Dockerfile"` 정확히 입력

**에러**: `Port not accessible` 또는 `502 Bad Gateway`
- ✅ 해결: `config/Dockerfile`의 CMD 확인 → `${PORT:-8000}` 사용하는지 확인

**에러**: `ANTHROPIC_API_KEY not found`
- ✅ 해결: Railway Variables 탭에서 정확히 입력했는지 확인 (공백 주의)

### GitHub Pages 정보 탭이 안 보임

**원인**: `_data/multimedia.json` 파일이 없음 (첫 요약 전)
- ✅ 자연스러운 상태: 첫 번째 요약 후 자동 생성됨

### Gmail 메일 못 받음

**확인 사항**:
1. `GMAIL_REFRESH_TOKEN` 유효한지 확인 → Railway 로그에서 에러 확인
2. Gmail 보안 설정 → "보안 수준이 낮은 앱" 허용 (deprecated → OAuth 2.0만 사용)
3. 발신자 주소 확인 → `GMAIL_USER`와 일치하는지 확인

---

## 📞 지원

문제 발생 시:
1. [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) "문제 해결" 섹션 확인
2. Railway Logs 탭에서 에러 메시지 확인
3. 필요시 [GitHub Issues](https://github.com/barobogi/260620_3_Multimedia_summary/issues) 등록

---

## 🎯 완성 기준

모든 항목이 완료되려면:

- ✅ Phase 1: Railway API가 `/api/health` 응답
- ✅ Phase 2: Gmail로 요약 메일 수신 (선택)
- ✅ Phase 3: GitHub Pages information.html에 데이터 표시
- ✅ Phase 4: 모바일에서 앱 실행 및 공유 (선택)
- ✅ Phase 5: 모든 테스트 PASSED (선택)

---

**예상 소요 시간**: 1~2시간

**시작 날짜**: 2026-06-20  
**목표 완료**: 2026-06-21
