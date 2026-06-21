# CHANGELOG — Multimedia Summary App

## v1.0 — 2026-06-21

### 최초 릴리즈

#### Added
- FastAPI 백엔드 — YouTube 동영상 요약 전체 파이프라인
- **Gemini 2.5 Flash** YouTube 네이티브 접근 (자막 추출 우회)
- Claude AI 구조화 요약 (요약 / 핵심 인사이트 / 카테고리 분류)
- Daum SMTP 자동 이메일 발송
- GitHub Pages 자동 카드 게시 (`information.html` Multimedia 탭)
- Flutter 모바일 앱 — 홈/로딩/결과 화면
- URL 붙여넣기 → 자동 요약 → 결과 확인 전체 흐름
- Render.com 클라우드 배포 (무료 플랜)
- 앱 아이콘 — 네이비 배경 + 재생 버튼 + AI 스파크 커스텀 디자인

#### Architecture
```
Flutter 앱 (YouTube URL 입력)
    ↓ POST /api/summarize
Render 서버 (Gemini 2.5 Flash → YouTube 영상 직접 이해)
    ↓ transcript text
Claude claude-sonnet-4-5 (구조화 요약)
    ↓
Daum 이메일 + GitHub Pages 동시 게시
```

---

## 개발 히스토리 (소급)

### 2026-06-20 — 초기 개발
- FastAPI 백엔드 기본 구조
- Railway 배포 시도 → Dockerfile 경로 오류 해결
- YouTube IP 차단 문제 최초 발견
- Railway → Render.com 이전 결정

### 2026-06-21 — 안정화 및 Gemini 전환
- Flutter APK 빌드 4단계 오류 해결
- AndroidManifest INTERNET 권한 추가 (release APK 필수)
- YouTube 자막 추출 5가지 방법 시도 후 실패
  - youtube_explode_dart (XmlParserException)
  - timedtext API (빈 응답)
  - cookie_jar 자동 세션 (빈 응답)
- **Gemini API 아키텍처 전환** — 근본 해결
- Claude 모델명 업데이트 (claude-3-5-sonnet-20241022 → claude-sonnet-4-5)
- .gitignore 수정 (frontend/lib/ 누락 해결)
- 앱 아이콘 커스텀 디자인
- v1.0 릴리즈

---

*자세한 디버깅 내역: `REF/debugging_LOG_Ver_20260620_v0.01.md` (이슈 #1 ~ #11)*
