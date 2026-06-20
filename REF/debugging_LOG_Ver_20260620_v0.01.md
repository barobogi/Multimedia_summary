# Debugging Log — Multimedia Summary App

**버전**: v0.01  
**날짜**: 2026-06-20  
**작성자**: Barobogi + Claude

---

## 🐛 이슈 #1 — Railway 배포 실패: Dockerfile 경로 오류

### 증상
```
scheduling build on Metal builder "production-builderv3-us-west1-9pcb"
unpacking archive
150 KB / 1ms
couldn't locate a dockerfile at path Dockerfile in code archive
uploading snapshot
35.5 KB
```
배포 소요 시간: **2초 만에 실패** (실제 빌드 시작조차 못 함)

### 원인
Railway는 기본적으로 레포 **루트**에서 `Dockerfile`을 찾는다.  
이 프로젝트는 Dockerfile이 `config/Dockerfile`에 있었고,  
`railway.json`의 설정이 잘못되어 Railway가 경로를 인식하지 못했다.

**잘못된 railway.json (원인):**
```json
{
  "build": {
    "builder": "dockerfile",      ← 소문자 (Railway는 대문자 요구)
    "dockerfile": "./config/Dockerfile"  ← 키 이름 오류 (dockerfilePath 여야 함)
  }
}
```

### 해결
`railway.json`을 올바른 Railway v2 스키마로 수정:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",           ← 대문자로 수정
    "dockerfilePath": "config/Dockerfile"  ← 올바른 키 이름으로 수정
  },
  "deploy": {
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 3
  }
}
```

**핵심 차이점:**

| 항목 | 잘못된 값 | 올바른 값 |
|------|-----------|-----------|
| builder 값 | `"dockerfile"` (소문자) | `"DOCKERFILE"` (대문자) |
| 경로 키 이름 | `"dockerfile"` | `"dockerfilePath"` |

### 결과
수정 후 master_watch.py 자동 push → Railway 재배포 → **Building 성공** (1분 이상 빌드 진행 중 = 정상)

### 교훈
- Railway `railway.json` 스키마는 **대소문자 구분** 엄격함
- `builder` 값은 반드시 대문자: `DOCKERFILE`, `NIXPACKS`, `HEROKU`
- Dockerfile이 서브폴더에 있을 경우 반드시 `dockerfilePath` 키 사용

---

---

## 🐛 이슈 #2 — Railway 앱 시작 실패: 환경변수 미주입

### 증상
```
pydantic_core._pydantic_core.ValidationError: 2 validation errors for Settings
anthropic_api_key
  Field required [type=missing, input_value={'port': '8080'}, input_type=dict]
github_token
  Field required [type=missing, input_value={'port': '8080'}, input_type=dict]
```
앱이 켜지자마자 크래시. `input_value={'port': '8080'}` — PORT 하나만 읽힘.

### 원인
Railway Variables 탭에서 입력한 변수들이 컨테이너에 주입되지 않았다.  
빌드/재배포 타이밍 문제로 변수가 유실된 것으로 추정.  
`pydantic-settings`가 `anthropic_api_key`, `github_token`을 required로 선언 → 앱 임포트 시점에 즉시 크래시.

### 해결 (코드)
`config.py`에서 required → Optional로 변경 (앱이 일단 시작되도록):
```python
# 변경 전
anthropic_api_key: str
github_token: str

# 변경 후
anthropic_api_key: Optional[str] = None
github_token: Optional[str] = None
```

`github_service.py`에서 모듈 로드 시 즉시 실행되던 `Github()` 호출을 함수 안으로 지연:
```python
# 변경 전 (모듈 로드 시 즉시 실행 → 크래시)
gh = Github(settings.github_token)

# 변경 후 (실제 호출 시점으로 지연)
def _gh():
    if not settings.github_token:
        raise RuntimeError("GITHUB_TOKEN이 설정되지 않았습니다")
    return Github(settings.github_token)
```

### 해결 (Railway)
Variables 탭에서 변수 7개 재입력 후 Redeploy.

### 교훈
- Railway Variables는 재배포 타이밍에 따라 유실될 수 있음 → 배포 후 Variables 탭에서 재확인 필수
- 프로덕션 앱은 필수 설정이 없어도 **시작은 되게** 만들고, 실제 호출 시점에 오류를 내는 것이 디버깅에 유리
- 모듈 로드 시 외부 서비스 연결(GitHub, DB 등) 즉시 실행 금지 → 함수로 지연

---

## 🐛 이슈 #3 — Railway 도메인 접속 불가: Public Domain 미생성

### 증상
```
Application failed to respond
This error appears to be caused by the application.
```
앱 내부(Console)에서는 정상 응답하지만 외부 URL로 접속 불가.

### 원인
Settings → Networking → Public Networking 섹션이 **비어있었음**.  
도메인 생성 과정에서 어느 시점에 도메인이 삭제되었고, 이후 재생성 없이 이전 URL로 계속 접속 시도.

### 진단 방법
Railway Console 탭에서 내부 테스트로 앱과 라우팅 문제를 분리:
```bash
# curl 없을 경우 Python으로 대체
python -c "import urllib.request; print(urllib.request.urlopen('http://localhost:8000/api/health').read())"
# → 내부 정상 응답 확인 → 라우팅 문제로 범위 좁힘
```

### 해결
Settings → Networking → **Generate Domain** → 포트 `8000` 입력 → 새 도메인 생성  
새 URL: `https://multimediasummary-production-55d7.up.railway.app`

### 결과
```json
{"status":"healthy","timestamp":"2026-06-20T13:05:04.145223","service":"Multimedia Summary API"}
```
✅ **배포 완전 성공**

### 교훈
- "Application failed to respond"는 앱 크래시와 라우팅 문제 두 가지 원인이 있음
- Railway Console에서 `localhost:PORT` 내부 테스트로 원인 분리 가능
- Railway Public Domain은 Settings → Networking에서 명시적으로 생성해야 함
- 도메인이 삭제되면 URL이 무효가 됨 (Railway가 알림을 주지 않음)

---

## 🐛 이슈 #4 — YouTube 자막 추출 실패: yt-dlp 포맷 오류 + 라이브러리 버전

### 증상
```
ERROR: Requested format is not available. Use --list-formats for a list of available formats
```
yt-dlp로 메타데이터 추출 시 Railway 서버에서 전 영상 동일 에러.

이후 `youtube_transcript_api` 로 전환했으나:
```
youtube_transcript_api._errors.TranscriptsDisabled:
Could not retrieve a transcript for the video ... Subtitles are disabled for this video
```
테스트한 모든 영상(4개)에서 동일하게 실패.

### 원인 1 — yt-dlp 메타데이터 추출 실패
Railway 서버 IP(Google Cloud 미국 리전)에서 yt-dlp가 YouTube 포맷 정보를 가져오지 못함.  
`download=False`여도 내부적으로 포맷 목록을 조회하는 과정에서 차단됨.

**해결**: yt-dlp 대신 **YouTube oEmbed API** 사용 (인증 불필요, IP 무관)
```python
# https://www.youtube.com/oembed?url=...&format=json
# → title, author_name(channel), thumbnail_url 반환
```

### 원인 2 — youtube_transcript_api 버전 차이로 클라우드 차단
| 환경 | 버전 | 내부 방식 | Railway에서 작동 |
|------|------|-----------|----------------|
| 로컬 | 1.2.4 | InnerTube API | ✅ |
| Railway | 0.6.3 | HTML 스크래핑 | ❌ 차단 |

로컬 테스트로 확인: `x1b2AdDmLhw` 영상이 로컬 1.2.4에서는 자막 정상 추출됨.

**해결**: `requirements.txt`에서 `youtube-transcript-api==0.6.3` → `1.2.4` 업그레이드  
1.x API 변경점:
```python
# 0.6.x (구버전)
YouTubeTranscriptApi.get_transcript(video_id, languages=['ko'])

# 1.x (신버전)
api = YouTubeTranscriptApi()
snippets = api.fetch(video_id, languages=['ko', 'en'])
text = " ".join(s.text for s in snippets)
```

### 교훈
- Railway(Google Cloud) IP는 YouTube HTML 스크래핑에 차단될 수 있음
- `youtube_transcript_api` 1.x는 InnerTube API 사용으로 이 문제 우회
- 클라우드 배포 시 라이브러리 버전이 로컬과 달라 동작 차이 발생 가능 → 명시적 버전 고정 필요
- YouTube 접근은 공식 API(oEmbed, InnerTube)를 사용하는 라이브러리가 스크래핑보다 안정적

---

## ✅ 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|-----------|
| 2026-06-20 | v0.01 | Railway Dockerfile 경로 오류 디버깅 및 해결 |
| 2026-06-20 | v0.01 | Railway 환경변수 미주입 + 앱 시작 실패 해결 |
| 2026-06-20 | v0.01 | Railway Public Domain 미생성으로 외부 접속 불가 해결 |
| 2026-06-20 | v0.01 | yt-dlp IP 차단 → oEmbed 전환, youtube_transcript_api 0.6.3→1.2.4 업그레이드 |

---

*다음 이슈 발생 시 이 파일에 ## 이슈 #5 로 추가*
