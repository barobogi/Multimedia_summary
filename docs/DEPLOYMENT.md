# Railway 배포 가이드

Multimedia Summary App을 Railway 클라우드에 배포하는 가이드입니다.

## 📋 사전 요구사항

- [Railway 계정](https://railway.app) (GitHub 계정으로 가입)
- [Railway CLI](https://docs.railway.app/guides/cli) 설치
- GitHub 리포지토리

## 🚀 1단계: 로컬 테스트

배포 전에 Docker로 로컬 테스트하세요.

```bash
# Docker 이미지 빌드
docker build -f config/Dockerfile -t multimedia-summary:latest .

# 컨테이너 실행
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY=your_key \
  -e GITHUB_TOKEN=your_token \
  multimedia-summary:latest

# 헬스 체크
curl http://localhost:8000/api/health
```

## 🌐 2단계: Railway에 배포

### 2.1 Railway 프로젝트 생성

```bash
# Railway CLI 로그인
railway login

# 새 프로젝트 생성
cd Multimedia_summary
railway init
```

### 2.2 GitHub 연동 (권장)

1. [Railway Dashboard](https://railway.app)에서 프로젝트 선택
2. **Settings** → **Git**
3. **Connect GitHub** 클릭
4. 리포지토리 선택
5. **Deploy on Push** 활성화

### 2.3 수동 배포

```bash
railway up
```

## 🔧 3단계: 환경 변수 설정

Railway Dashboard에서:

1. **Variables** 탭 열기
2. 다음 환경 변수 추가:

### 필수 변수

```
ANTHROPIC_API_KEY=sk-ant-v1-xxxxx...
GITHUB_TOKEN=ghp_xxxxx...
GITHUB_REPO=barobogi/Daily_for_Barobogi
GITHUB_USERNAME=barobogi
GMAIL_USER=barobogi79@gmail.com
GMAIL_REFRESH_TOKEN=1//0xxxxx...
```

### 선택 변수

```
DEBUG=False
LOG_LEVEL=INFO
DRIVE_TYPE=onedrive
DRIVE_FOLDER_ID=xxxxx...
```

## 📝 환경 변수 가져오기

로컬 `.env` 파일에서 Railway로 변수를 가져오려면:

```bash
# .env 파일이 있으면
cat backend/.env | while IFS='=' read -r key value; do
  if [ -n "$key" ] && [[ "$key" != \#* ]]; then
    railway variables set "$key=$value"
  fi
done
```

## ✅ 4단계: 배포 확인

### 4.1 로그 확인

```bash
railway logs
```

예상 출력:
```
2026-06-20 12:00:00 🚀 Multimedia Summary API starting...
2026-06-20 12:00:01 Uvicorn running on http://0.0.0.0:8000
```

### 4.2 API 테스트

```bash
# 배포된 API URL 얻기
DEPLOYED_URL=$(railway env | grep RAILWAY_PUBLIC_DOMAIN)

# 헬스 체크
curl https://$DEPLOYED_URL/api/health

# 요약 테스트
curl -X POST https://$DEPLOYED_URL/api/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.youtube.com/watch?v=...",
    "platform": "youtube",
    "language": "ko"
  }'
```

### 4.3 Metrics 확인

Railway Dashboard:
- **Deployments** → 최신 배포 클릭
- **Logs** → 에러 확인
- **Metrics** → CPU, 메모리, 네트워크 모니터링

## 🔄 5단계: CI/CD 설정 (Optional)

### GitHub Actions 배포 자동화

`.github/workflows/deploy.yml`:

```yaml
name: Deploy to Railway

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Railway
        uses: addnab/docker-run-action@v3
        with:
          image: railway/cli:latest
          options: -v ${{ github.workspace }}:/workspace
          run: |
            railway login --token ${{ secrets.RAILWAY_TOKEN }}
            railway up
```

Railway에서 토큰 생성:
1. Dashboard → Account → Tokens
2. **Create Token** 클릭
3. GitHub Secrets에 `RAILWAY_TOKEN` 추가

## 🔗 6단계: 커스텀 도메인 설정 (Optional)

### 6.1 도메인 연결

1. Railway Dashboard → **Settings** → **Custom Domain**
2. 도메인 입력 (예: `api.barobogi.me`)
3. DNS 레코드 추가

### 6.2 SSL/TLS

Railway는 자동 SSL 제공 (Let's Encrypt)

## 📊 모니터링

### Railway 대시보드

- **Deployments**: 배포 이력
- **Logs**: 실시간 로그
- **Metrics**: 성능 지표
- **Usage**: 요금 정보

### 권장 설정

```bash
# 헬스 체크 활성화
railway variables set HEALTHCHECK=true

# 자동 재시작
railway variables set RESTART_POLICY=always

# 최대 재시도
railway variables set RESTART_MAX_RETRIES=3
```

## 🐛 문제 해결

### 배포 실패

**에러**: `Dockerfile not found`
```bash
# railway.json 확인
cat railway.json | grep dockerfile

# 수정
railway variables set DOCKERFILE_PATH=./config/Dockerfile
```

**에러**: `PORT not accessible`
```bash
# Dockerfile CMD 확인
# CMD는 $PORT 환경 변수 사용해야 함
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
```

### 앱 크래시

**체크리스트**:
- ✅ 모든 필수 환경 변수 설정됐는가?
- ✅ API 키가 유효한가?
- ✅ Python 버전 호환성 (3.11+)
- ✅ 의존성 설치됐는가? (requirements.txt)

```bash
# 로그에서 에러 확인
railway logs --tail=100
```

### 응답 느림

**원인**: Railway 무료 플랜 제한
- 메모리: 512MB
- 동시 요청: 제한됨
- 최대 실행 시간: 30초

**해결**:
1. 유료 플랜 업그레이드
2. 요청 타임아웃 최적화
3. 배경 작업 큐 (Celery) 구현

## 📈 성능 최적화

### 1. 응답 캐싱

```python
# backend/app/cache.py
from functools import lru_cache
from datetime import timedelta

@lru_cache(maxsize=100)
def cache_summary(video_id: str, ttl: int = 3600):
    # 캐시 로직
    pass
```

### 2. 배경 작업

```python
# 메일/GitHub 업데이트를 백그라운드에서 처리
background_tasks.add_task(distribute_summary, summary)
```

### 3. 데이터베이스 (Optional)

Railway의 PostgreSQL 추가:
```bash
railway add postgres
```

## 💳 요금

**Railway 무료 플랜**:
- 월 5달러 크레딧 = 약 500시간 실행
- 충분함 (매달 15시간 사용 시 33개월 사용 가능)

**추가 크레딧 필요 시**:
- 실행 시간 : $0.01/시간
- 저장소 : $1/GB/월
- 네트워크 : $0.1/GB

## 🚨 보안 체크리스트

- [ ] `.env` 파일 `.gitignore`에 추가
- [ ] API 키 노출 안 됨
- [ ] HTTPS 활성화 (기본)
- [ ] CORS 설정 확인
- [ ] Rate limiting 구현
- [ ] 정기적 로그 검토

## 📚 참고 문서

- [Railway 공식 문서](https://docs.railway.app)
- [Railway CLI 가이드](https://docs.railway.app/guides/cli)
- [Railway 환경 변수](https://docs.railway.app/guides/environment-variables)
- [Dockerfile 작성 가이드](https://docs.docker.com/engine/reference/builder)

## ❓ FAQ

**Q: Railway에서 최대 실행 시간이 30초인데, 요약이 오래 걸리면?**
A: 배경 작업 큐(Celery) 구현하거나, 요약을 비동기로 처리

**Q: 배포 후 환경 변수 변경하면?**
A: Railway가 자동으로 앱 재배포 (또는 `railway up`)

**Q: Railway 무료 플랜에서 다른 서비스도 가능한가?**
A: PostgreSQL, Redis 등 추가 가능 (크레딧 사용)

**Q: 다운타임 없이 배포하려면?**
A: GitHub Actions + Rolling Deployment 설정

---

**배포 완료!** 🎉

배포된 API: `https://<project-name>.railway.app/api/health`

다음 단계: [GitHub Pages 정보 탭 추가](../README.md#github-pages)
