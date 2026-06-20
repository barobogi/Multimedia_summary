# 개발 환경 설정 가이드

Multimedia Summary App 개발을 위한 환경 설정 방법입니다.

## 📋 요구사항

- **Python**: 3.11 이상
- **Node.js**: 16.x 이상 (선택사항)
- **Flutter**: 3.x 이상
- **Docker**: 선택사항 (로컬 테스트용)
- **Git**: 최신 버전

## 1️⃣ 백엔드 설정

### 1.1 Python 가상 환경 생성

```bash
cd backend

# 가상 환경 생성
python -m venv venv

# 활성화
source venv/bin/activate        # macOS/Linux
# or
venv\Scripts\activate           # Windows
```

### 1.2 의존성 설치

```bash
pip install -r requirements.txt
```

### 1.3 환경 변수 설정

```bash
cp .env.example .env
```

`.env` 파일을 편집하여 다음 항목을 설정하세요:

#### 필수 항목

**Claude API**
```
ANTHROPIC_API_KEY=sk-ant-v1-xxxxx...
```
- [Anthropic Console](https://console.anthropic.com/)에서 발급
- API 키 생성 → 복사

**GitHub Token**
```
GITHUB_TOKEN=ghp_xxxxx...
GITHUB_REPO=barobogi/Daily_for_Barobogi
GITHUB_USERNAME=barobogi
```
- [GitHub Settings → Tokens](https://github.com/settings/tokens)에서 발급
- Scopes: `repo`, `workflow`, `gist`

#### Gmail API 설정

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 새 프로젝트 생성
3. Gmail API 활성화
4. OAuth 2.0 클라이언트 ID 생성
   - 응용 프로그램 유형: 데스크톱
   - `credentials.json` 다운로드

5. 첫 번째 실행 시 인증
```python
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/gmail.send']
flow = InstalledAppFlow.from_client_secrets_file(
    'credentials.json', SCOPES)
creds = flow.run_local_server(port=0)
```

6. `.env` 파일에 저장
```
GMAIL_USER=barobogi79@gmail.com
GMAIL_REFRESH_TOKEN=1//0xxxxxx...
GMAIL_CLIENT_ID=xxxxx...
GMAIL_CLIENT_SECRET=xxxxx...
```

#### OneDrive/Google Drive (선택)

Obsidian vault가 클라우드에 있는 경우:

```
DRIVE_TYPE=onedrive          # or 'google'
DRIVE_FOLDER_ID=xxxxx...
DRIVE_REFRESH_TOKEN=xxxxx...
```

### 1.4 로컬 실행

```bash
python main.py
```

- API: http://localhost:8000
- 문서: http://localhost:8000/docs (Swagger UI)

## 2️⃣ Flutter 앱 설정

### 2.1 Flutter SDK 설치

```bash
# macOS (Homebrew)
brew install flutter

# or 수동 설치: https://flutter.dev/docs/get-started/install
```

### 2.2 플러터 의존성 확인

```bash
flutter doctor
```

모두 ✓ 표시되는지 확인하세요.

### 2.3 프로젝트 설정

```bash
cd frontend

# 의존성 설치
flutter pub get

# Android 플랫폼 설정
cd android
./gradlew clean
cd ..
```

### 2.4 개발 실행

**에뮬레이터로 실행**
```bash
flutter emulators --launch Pixel_5_API_31
flutter run
```

**실기기로 실행**
```bash
flutter run
# 휴대폰 연결 후 자동 감지
```

### 2.5 APK 빌드

**Debug APK**
```bash
flutter build apk --debug
# 생성 위치: build/app/outputs/apk/debug/app-debug.apk
```

**Release APK**
```bash
# 먼저 키스토어 생성 (처음 한 번)
keytool -genkey -v -keystore ~/key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias key

# Release APK 빌드
flutter build apk --release
# 생성 위치: build/app/outputs/apk/release/app-release.apk
```

## 3️⃣ Docker로 로컬 테스트

### 3.1 컨테이너 실행

```bash
docker-compose -f config/docker-compose.yml up
```

- API: http://localhost:8000
- 로그: `docker-compose logs -f api`

### 3.2 컨테이너 중지

```bash
docker-compose -f config/docker-compose.yml down
```

## 4️⃣ Railway 배포

### 4.1 Railway 계정 생성

https://railway.app/ 에서 GitHub 계정으로 가입

### 4.2 프로젝트 생성

```bash
npm i -g @railway/cli
railway login

cd Multimedia_summary
railway init
```

### 4.3 환경 변수 설정

Railway Dashboard에서:
1. 프로젝트 선택
2. Variables 탭
3. 필요한 환경 변수 입력 (.env 참고)

### 4.4 배포

```bash
railway up
```

또는 GitHub Push시 자동 배포:
1. GitHub 연동
2. 자동 배포 설정 활성화

## 🧪 테스트

### 백엔드 API 테스트

```bash
# 헬스 체크
curl http://localhost:8000/api/health

# 요약 생성 (샘플)
curl -X POST http://localhost:8000/api/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.youtube.com/watch?v=...",
    "platform": "youtube",
    "language": "ko"
  }'
```

### 단위 테스트

```bash
cd backend
pytest tests/ -v
```

### 통합 테스트

```bash
cd backend
pytest tests/integration/ -v
```

## 🔍 트러블슈팅

### Python 라이브러리 에러

```bash
# 캐시 삭제 후 재설치
pip cache purge
pip install -r requirements.txt --force-reinstall
```

### YouTube 자막 추출 실패

- 자막이 없는 동영상은 처리 불가
- YouTube 정책 변경 시 yt-dlp 업데이트 필요
```bash
pip install --upgrade yt-dlp
```

### Gmail API 인증 오류

- 토큰 만료: `GMAIL_REFRESH_TOKEN` 갱신 필요
- OAuth 동의 화면 구성: Google Cloud Console에서 확인

### Flutter 빌드 오류

```bash
flutter clean
rm -rf build/
flutter pub get
flutter run
```

## 📚 참고 문서

- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [Flutter 문서](https://flutter.dev/docs)
- [Claude API 문서](https://anthropic.com/api)
- [YouTube API 문서](https://developers.google.com/youtube/v3)
- [yt-dlp GitHub](https://github.com/yt-dlp/yt-dlp)

## 💡 팁

1. **개발 속도**: 핫 리로드 활용
   ```bash
   flutter run
   # 앱 실행 중에 's'를 누르면 핫 리로드
   ```

2. **API 테스트**: Swagger UI 활용
   - http://localhost:8000/docs
   - "Try it out" 버튼으로 직접 테스트

3. **로깅 상세화**
   ```python
   # main.py
   logging.basicConfig(level=logging.DEBUG)
   ```

4. **환경별 .env 파일**
   ```
   .env.local       # 로컬 개발
   .env.railway     # Railway 배포
   .env.test        # 테스트
   ```

## ❓ 문제 해결

문제가 발생하면:
1. [Troubleshooting.md](TROUBLESHOOTING.md) 확인
2. 로그 확인: `docker-compose logs -f api`
3. GitHub Issues 검색
4. 새 Issue 등록
