# Multimedia Summary App

동영상을 공유하면 AI가 요약하고 여러 채널로 자동 배포하는 모바일 앱입니다.

**상태**: 🚧 1차 개발 진행 중 (2026-06-20~)

## 🎯 주요 기능

1. **YouTube 영상 링크 공유** - 앱 공유 인텐트로 링크 캡처
2. **AI 기반 요약** - Claude API로 요약 생성 및 인사이트 추출
3. **카테고리 분류** - 주식, AI, 학습 등 자동 태깅
4. **다중 채널 배포**
   - 📧 Gmail로 요약 메일 발송
   - 📝 Obsidian 마크다운 저장 (GitHub 동기화)
   - 🌐 GitHub Pages 자동 업데이트

## 📁 프로젝트 구조

```
.
├── backend/                    # FastAPI 백엔드 (Python)
│   ├── app/
│   │   ├── routes/            # API 엔드포인트
│   │   │   ├── health_router.py
│   │   │   └── summarize_router.py
│   │   ├── services/          # 비즈니스 로직
│   │   │   ├── youtube_service.py
│   │   │   ├── claude_service.py
│   │   │   ├── gmail_service.py
│   │   │   ├── obsidian_service.py
│   │   │   └── github_service.py
│   │   ├── models.py          # Pydantic 모델
│   │   └── config.py          # 환경 설정
│   ├── main.py                # FastAPI 애플리케이션
│   ├── requirements.txt
│   └── .env.example
│
├── frontend/                   # Flutter APK
│   ├── lib/
│   ├── android/
│   ├── pubspec.yaml
│   └── [Flutter 프로젝트]
│
├── docs/                       # 문서
│   ├── SETUP.md               # 환경 설정 가이드
│   ├── API.md                 # API 문서
│   └── DEPLOYMENT.md          # 배포 가이드
│
├── config/                     # 배포 설정
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── railway.json
│
├── DEV_PLAN_PHASE1.md         # 1차 개발 계획서
└── README.md                  # 이 파일

```

## 🏗️ 아키텍처

```
YouTube → [공유] → Flutter APK
                     ↓ HTTPS
                Railway 클라우드
                (Python FastAPI)
                ├── yt-dlp (자막 추출)
                ├── Claude API (요약/분석)
                ├── Gmail API (메일)
                ├── GitHub API (Pages 업데이트)
                └── OneDrive/Drive API (Obsidian 동기화)
```

## 🚀 빠른 시작

### 1. 백엔드 로컬 실행

```bash
cd backend

# 환경 설정
python -m venv venv
source venv/bin/activate          # macOS/Linux
# or
venv\Scripts\activate             # Windows

pip install -r requirements.txt

# .env 파일 생성 및 API 키 입력
cp .env.example .env
# 필수: ANTHROPIC_API_KEY, GITHUB_TOKEN

# 서버 실행
python main.py
# http://localhost:8000/docs 에서 API 테스트
```

### 2. Flutter APK 개발

```bash
cd frontend
flutter pub get
flutter run
```

## 🔧 기술 스택

| 레이어 | 기술 | 버전 |
|--------|------|------|
| **Frontend** | Flutter | 3.x |
| **Backend** | FastAPI | 0.115+ |
| **Python** | Python | 3.11+ |
| **AI** | Claude API | claude-3.5-sonnet |
| **Hosting** | Railway | - |
| **VCS** | GitHub | - |

## 📋 API 엔드포인트

### 헬스 체크
```bash
GET /api/health
GET /api/health/ready
```

### 요약 생성 (핵심)
```bash
POST /api/summarize

Body:
{
  "video_url": "https://youtube.com/watch?v=...",
  "platform": "youtube",
  "language": "ko"
}

Response:
{
  "summary": {
    "metadata": {...},
    "summary": "요약 텍스트",
    "key_insights": [...],
    "categories": ["AI", "Stock"],
    "stock_related": [...],
    "timestamp": "2026-06-20T..."
  },
  "distribution": {
    "email_sent": true,
    "obsidian_saved": true,
    "github_pages_updated": true
  }
}
```

Swagger UI: http://localhost:8000/docs

## 🔐 환경 변수

[docs/SETUP.md](docs/SETUP.md) 참조

**필수:**
- `ANTHROPIC_API_KEY` - Claude API
- `GITHUB_TOKEN` - GitHub Personal Access Token
- `GMAIL_USER`, `GMAIL_REFRESH_TOKEN` - Gmail API

**선택:**
- `DRIVE_TYPE`, `DRIVE_FOLDER_ID` - OneDrive/Google Drive

## 📦 배포

### Railway (클라우드)
```bash
railway login
railway up
```

### Docker (로컬)
```bash
docker-compose up
```

## 🧪 테스트

```bash
# 백엔드 단위 테스트
cd backend
pytest tests/

# 통합 테스트
pytest tests/integration/

# Flutter 테스트
cd frontend
flutter test
```

## 📖 문서

- [SETUP.md](docs/SETUP.md) - 개발 환경 설정
- [DEV_PLAN_PHASE1.md](DEV_PLAN_PHASE1.md) - 1차 개발 계획
- [API.md](docs/API.md) - API 상세 문서

## 🐛 문제 해결

[Troubleshooting Guide](docs/TROUBLESHOOTING.md) 참조

## 📈 진행 상황

| Phase | 상태 | 항목 |
|-------|------|------|
| 1.1 | ✅ 완료 | 기본 흐름 (요약 생성 + Gmail) |
| 1.2 | 🔄 진행 중 | Obsidian + GitHub Pages |
| 1.3 | ⬜ 예정 | 스마트 분석 (카테고리 태깅) |
| UI/UX | 🔄 진행 중 | Flutter APK 개발 |

## 👨‍💻 기여

문제 리포팅 및 제안: [GitHub Issues](https://github.com/barobogi/Multimedia_summary/issues)

## 📝 라이선스

MIT License

## 📞 연락처

- Email: barobogi79@gmail.com
- Website: https://barobogi.github.io/Daily_for_Barobogi/
