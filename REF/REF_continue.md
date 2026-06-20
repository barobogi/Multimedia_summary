# Multimedia Summary App - 지속 개발 문서

**작성일**: 2026-06-20  
**Phase**: 1차 개발 진행 중  
**상태**: 백엔드 기본 구조 완성, Flutter APK 개발 예정

## 📊 완료 항목

### ✅ Phase 1.1 기본 흐름 (완료)
- [x] FastAPI 백엔드 프로젝트 초기화
- [x] YouTube 자막 추출 엔드포인트
- [x] Claude API 요약/분석 로직
- [x] Gmail 자동 발송 기능
- [x] Obsidian 마크다운 저장 (GitHub API)
- [x] GitHub Pages 자동 업데이트
- [x] 프로젝트 폴더 구조 및 설정 파일
- [x] README.md 및 SETUP.md 작성
- [x] Docker 및 배포 설정

## 🚀 다음 작업 (우선순위)

### 1️⃣ Flutter APK 개발 (진행 중)

#### 1.1 프로젝트 초기화
```bash
cd frontend
flutter create --project-name multimedia_summary .

# 또는 이미 있으면
flutter pub get
```

#### 1.2 공유 Intent 수신 설정

**Android** (`android/app/src/main/AndroidManifest.xml`)
```xml
<intent-filter>
    <action android:name="android.intent.action.SEND" />
    <category android:name="android.intent.category.DEFAULT" />
    <data android:mimeType="text/plain" />
</intent-filter>
```

**iOS** (`ios/Runner/Info.plist`)
```xml
<key>NSLocalNetworkUsageDescription</key>
<string>이 앱은 동영상 링크를 처리하기 위해 네트워크 접근이 필요합니다.</string>
```

#### 1.3 UI 구성
- 메인 화면: URL 입력 + 클립보드 자동 감지
- 로딩 화면: 진행률 표시
- 결과 화면: 요약, 인사이트, 카테고리 표시
- 히스토리 화면: 저장된 항목 목록

#### 1.4 백엔드 API 통신
```dart
final response = await http.post(
  Uri.parse('https://your-railway-app.up.railway.app/api/summarize'),
  body: jsonEncode({'video_url': url}),
);
```

### 2️⃣ 웹사이트 Information 탭 추가

GitHub Pages 리포지토리에서:

#### 2.1 새로운 HTML 파일 생성
`_includes/multimedia-list.html` 또는 `multimedia.html`

#### 2.2 Jekyll 데이터 활용
`_data/multimedia.json` (FastAPI에서 자동 생성)

#### 2.3 웹사이트 레이아웃 수정
Navigation에 "Multimedia" 탭 추가

### 3️⃣ Railway 배포 준비

#### 3.1 배포 가이드 작성
`docs/DEPLOYMENT.md`

```bash
# 배포 체크리스트
- [ ] Railway 계정 생성
- [ ] GitHub 연동
- [ ] 환경 변수 설정
- [ ] 헬스 체크 확인
- [ ] API 테스트
```

#### 3.2 CI/CD 파이프라인
`.github/workflows/deploy.yml` 생성

### 4️⃣ 테스트 및 문서화

#### 4.1 백엔드 테스트
```python
# backend/tests/
test_health.py
test_youtube_extraction.py
test_claude_summarization.py
test_distribution.py
```

#### 4.2 Flutter 테스트
```dart
// frontend/test/
widget_test.dart
integration_test/
```

#### 4.3 API 문서
`docs/API.md` - Swagger 스키마 기반 문서화

### 5️⃣ 성능 최적화

#### 5.1 캐싱
- Redis 또는 로컬 SQLite 캐싱
- 중복 요청 방지

#### 5.2 요청 큐잉
- 백그라운드 작업 (Celery 또는 APScheduler)
- 배포 재시도 로직

#### 5.3 모니터링
- 에러 추적 (Sentry)
- 성능 모니터링 (DataDog, New Relic)

## 📁 생성해야 할 파일들

### 문서
```
docs/
├── SETUP.md                  ✅ 완료
├── API.md                    ⬜ 필요
├── DEPLOYMENT.md             ⬜ 필요
├── TROUBLESHOOTING.md        ⬜ 필요
└── ARCHITECTURE.md           ⬜ 필요
```

### 백엔드 테스트
```
backend/tests/
├── __init__.py
├── conftest.py
├── test_health.py
├── test_youtube_service.py
├── test_claude_service.py
├── test_gmail_service.py
├── test_obsidian_service.py
├── test_github_service.py
└── integration/
    └── test_full_flow.py
```

### Flutter
```
frontend/
├── lib/
│   ├── screens/
│   │   ├── home_screen.dart
│   │   ├── loading_screen.dart
│   │   ├── result_screen.dart
│   │   └── history_screen.dart
│   ├── services/
│   │   ├── api_service.dart
│   │   └── storage_service.dart
│   ├── models/
│   │   ├── summary_model.dart
│   │   └── video_metadata_model.dart
│   ├── main.dart
│   └── themes/
│       └── app_theme.dart
├── test/
│   ├── widget_test.dart
│   └── unit_test.dart
├── integration_test/
│   └── app_test.dart
└── pubspec.yaml
```

### CI/CD
```
.github/workflows/
├── backend-test.yml
├── flutter-test.yml
└── deploy.yml
```

## 🔄 개발 순서

```
Week 1-2: Flutter APK 기본 구조
  ├─ Intent 수신
  ├─ UI 화면 구성
  └─ API 통신

Week 2-3: 통합 테스트 및 배포
  ├─ Railway 배포
  ├─ GitHub Pages 업데이트
  └─ 웹사이트 Information 탭

Week 3-4: 성능 최적화 및 문서화
  ├─ 캐싱 구현
  ├─ 테스트 커버리지 증가
  └─ API 문서 작성

Week 4+: 고급 기능
  ├─ 오프라인 모드
  ├─ 여러 플랫폼 지원
  └─ 커스터마이징
```

## 🎯 1차 개발 완료 기준

- [x] 백엔드: YouTube → Claude → Gmail/GitHub/Obsidian 전체 흐름
- [ ] Flutter: APK 빌드 및 실행 가능
- [ ] 배포: Railway에서 정상 작동
- [ ] 웹사이트: Information 탭 추가
- [ ] 문서: API, 배포, 트러블슈팅 가이드
- [ ] 테스트: 백엔드 + Flutter 단위 테스트

## 💾 저장된 메모리

**프로젝트 정보**: `memory/project_multimedia_summary.md`
- 앱 개요 및 기능
- 기술 스택
- 배포 채널

**개발 계획**: `DEV_PLAN_PHASE1.md`
- 상세 아키텍처
- 기술 스택 선택 이유
- MVP 정의 및 일정

## 🔗 관련 링크

- **GitHub**: https://github.com/barobogi/Daily_for_Barobogi
- **Barobogi Website**: https://barobogi.github.io/Daily_for_Barobogi/
- **Railway**: https://railway.app
- **Claude API**: https://anthropic.com/api
- **Flutter**: https://flutter.dev

## 📌 주의사항

1. **API 키 보안**
   - .env 파일 절대 커밋 금지
   - Railway에서만 환경 변수 설정
   - 토큰 주기적 갱신

2. **GitHub API 제한**
   - 인증되지 않은 요청: 시간당 60개
   - 인증된 요청: 시간당 5000개
   - 캐싱으로 불필요한 요청 줄이기

3. **YouTube API 비용**
   - 일일 사용량 제한: 월 1000만 units
   - 동영상 조회: 1 unit
   - 자막 다운로드: yt-dlp로 무료 처리

4. **Claude API 비용**
   - 토큰 기반 가격
   - 장문 요약은 비용 많음
   - 배치 처리 고려

## ✉️ 연락처

Barobogi  
Email: barobogi79@gmail.com  
Website: https://barobogi.github.io/Daily_for_Barobogi/

---

*마지막 업데이트: 2026-06-20*  
*다음 작업: Flutter APK 프로젝트 초기화*
