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

## ✅ 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|-----------|
| 2026-06-20 | v0.01 | Railway Dockerfile 경로 오류 디버깅 및 해결 |
| 2026-06-20 | v0.01 | Railway 환경변수 미주입 + 앱 시작 실패 해결 |
| 2026-06-20 | v0.01 | Railway Public Domain 미생성으로 외부 접속 불가 해결 |

---

*다음 이슈 발생 시 이 파일에 ## 이슈 #4 로 추가*
