# Multimedia Summary App - 1차 개발 계획

## 아키텍처 개요

```
YouTube 앱 → [공유] → Flutter APK
                       ↓ HTTPS
                Railway 무료 클라우드
                (Python FastAPI 서버)
                ├── YouTube 자막 추출
                ├── Claude API 요약/분석
                ├── Gmail 발송
                ├── GitHub Pages 업데이트
                └── Obsidian 폴더 동기화 (OneDrive/GDrive API)
```

## 기술 스택

| 레이어 | 기술 | 이유 |
|--------|------|------|
| **Frontend** | Flutter (Dart) | iOS/Android 동시 지원, 빠른 개발 |
| **Backend** | Python FastAPI | 가벼움, 비동기 지원, 배포 용이 |
| **호스팅** | Railway | 무료 플랜 월 500시간, 자동 배포 |
| **AI** | Claude API | 고품질 요약 및 분석 |
| **배포 채널** | Gmail, GitHub Pages, OneDrive | 자동화 가능 |

## MVP (Minimum Viable Product) 정의

### Phase 1.1: 기본 흐름 (2주)
- [ ] Flutter APK: 동영상 링크 공유 받기
- [ ] FastAPI 서버: 링크 검증 및 메타데이터 추출
- [ ] Claude API 연동: 기본 요약 생성
- [ ] Gmail 발송: 요약 내용 자동 메일

### Phase 1.2: 배포 기능 확장 (2주)
- [ ] Obsidian API: 로컬 폴더 동기화 (OneDrive 연동)
- [ ] GitHub Pages: 웹사이트에 최근 게시물 추가
- [ ] 메타데이터: 제목, URL, 타임스탬프 자동 기록

### Phase 1.3: 스마트 분석 (1주)
- [ ] 주식/자본 관련 내용 태깅 및 강조
- [ ] AI 인사이트 자동 추출
- [ ] 카테고리별 섹션 구분 (학습/투자/기타)

---

## 세부 작업 분해

### 백엔드 (FastAPI 서버)

**1.1 프로젝트 초기화**
- [ ] Railway 계정 설정 및 배포 환경 구성
- [ ] Python 3.11 + FastAPI 프로젝트 생성
- [ ] `.env` 파일 (Claude API key, Gmail 토큰 등)
- [ ] GitHub 연동 배포 설정

**1.2 링크 처리 엔드포인트**
```python
POST /api/summarize
{
  "video_url": "https://youtube.com/watch?v=...",
  "platform": "youtube"
}
```
- [ ] 유튜브 URL 검증
- [ ] yt-dlp로 메타데이터 추출 (제목, 채널, 설명)
- [ ] YouTube 자막 추출

**1.3 Claude API 연동**
```python
- 입력: 자막 텍스트
- 출력: {
    "summary": "...",
    "key_insights": [...],
    "stock_related": [...],
    "categories": ["AI", "Stock", "Learning"]
  }
```
- [ ] Claude Haiku 또는 Sonnet 선택
- [ ] 프롬프트 템플릿 작성 (한국어 최적화)
- [ ] 토큰 제한 처리 (길 동영상 대응)

**1.4 Gmail 자동 발송**
- [ ] Gmail API 설정 (OAuth 2.0)
- [ ] HTML 이메일 템플릿 작성
- [ ] 발송 로직 및 재시도 메커니즘

**1.5 Obsidian 동기화**
- [ ] OneDrive/Google Drive API 연동
- [ ] Markdown 파일 생성 (YAML frontmatter)
- [ ] 로컬 폴더 구조: `/Multimedia/{date}/{title}.md`

**1.6 GitHub Pages 업데이트**
- [ ] Jekyll 데이터 파일 또는 정적 JSON 생성
- [ ] GitHub API로 `_posts/` 또는 `_data/` 업데이트
- [ ] 웹사이트 빌드 자동화 (GitHub Actions)

---

### 프론트엔드 (Flutter APK)

**2.1 프로젝트 초기화**
- [ ] Flutter 프로젝트 생성
- [ ] android/ 폴더 구성 (compileSdkVersion 34+)
- [ ] iOS 폴더 구성 (Deployment Target 12.0+)

**2.2 공유 Intent 수신**
```kotlin
// android/app/src/main/AndroidManifest.xml
<intent-filter>
  <action android:name="android.intent.action.SEND" />
  <category android:name="android.intent.category.DEFAULT" />
  <data android:mimeType="text/plain" />
</intent-filter>
```
- [ ] Dart에서 수신한 URL 파싱
- [ ] URL 유효성 검증

**2.3 UI/UX**
- [ ] 메인 화면: URL 입력 / 클립보드 자동 감지
- [ ] 로딩 화면: 진행률 표시
- [ ] 결과 화면: 요약, 인사이트, 배포 상태 표시
- [ ] 저장된 항목 목록 (로컬 DB 또는 Firebase)

**2.4 백엔드 연동**
```dart
final response = await http.post(
  Uri.parse('https://your-railway-app.up.railway.app/api/summarize'),
  body: jsonEncode({'video_url': url}),
);
```
- [ ] FastAPI 서버와 HTTPS 통신
- [ ] 에러 처리 및 재시도 로직
- [ ] 로컬 캐싱 (중복 요청 방지)

**2.5 빌드 및 배포**
- [ ] APK 서명 설정
- [ ] GitHub Releases 또는 Firebase App Distribution

---

## 환경 설정 체크리스트

### 서버
- [ ] Railway 계정 및 결제 설정
- [ ] Claude API Key 발급
- [ ] Gmail App Password 생성
- [ ] GitHub Personal Access Token (for API)
- [ ] OneDrive/Google Drive Service Account (for Obsidian sync)

### 로컬 개발
- [ ] Python 3.11 설치
- [ ] Flutter SDK 설치 및 환경 변수 설정
- [ ] Android Studio + 에뮬레이터 또는 실기기
- [ ] Git & GitHub 연동

---

## 데이터 플로우 예시

```
1. 사용자가 YouTube 링크 공유
   ↓
2. Flutter APK가 Intent 수신
   ↓
3. "요약하기" 클릭
   ↓
4. POST /api/summarize → Railway 서버
   ↓
5. yt-dlp로 자막 추출
   ↓
6. Claude API로 요약/분석
   ↓
7. 병렬 처리:
   ├─ Gmail 발송 → barobogi79@gmail.com
   ├─ Obsidian 저장 → OneDrive
   └─ GitHub Pages 업데이트
   ↓
8. 결과를 APK 화면에 표시
```

---

## 일정 예상

| Phase | 기간 | 산출물 |
|-------|------|--------|
| 1.1 기본 흐름 | 2주 | 작동하는 요약 생성 + Gmail 발송 |
| 1.2 배포 확장 | 2주 | Obsidian + GitHub Pages 통합 |
| 1.3 스마트 분석 | 1주 | 카테고리 태깅 및 인사이트 |
| 버그 수정 및 최적화 | 1주 | 안정화 및 UX 개선 |
| **총 소요 기간** | **6주** | **Production-ready APK** |

---

## 다음 단계

1. ✅ 웹사이트 구조 확인
2. ⬜ FastAPI 프로젝트 초기화 및 Railway 배포
3. ⬜ YouTube 자막 추출 모듈 개발
4. ⬜ Claude API 프롬프트 최적화
5. ⬜ Flutter APK 기본 구조 구성

---

## 참고 자료

- YouTube Data API: https://developers.google.com/youtube/v3
- yt-dlp: https://github.com/yt-dlp/yt-dlp
- FastAPI: https://fastapi.tiangolo.com/
- Flutter: https://flutter.dev/
- Railway: https://railway.app/
- Claude API: https://anthropic.com/api
