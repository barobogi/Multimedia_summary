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

## 🐛 이슈 #5 — Railway(Google Cloud) IP → YouTube 완전 차단 + Webshare 무료 프록시 실패

### 증상
```
youtube_transcript_api._errors.RequestBlocked:
YouTube is blocking requests from your IP.
You are doing requests from an IP belonging to a cloud provider
(like AWS, Google Cloud Platform, Azure, etc.)
```
이후 Webshare 프록시 적용 시:
```
urllib3.exceptions.ResponseError: too many 429 error responses
HTTPSConnectionPool(host='www.youtube.com', port=443): Max retries exceeded
```

### 원인 분석

**원인 1 — Railway = Google Cloud IP**
Railway는 내부적으로 Google Cloud Platform(GCP) 인프라를 사용.  
YouTube는 GCP, AWS, Azure 등 클라우드 IP 대역을 DB로 관리하며 자막 API 요청을 차단.  
`youtube_transcript_api` 0.6.x에서는 "Subtitles are disabled" 에러로 위장되다가  
1.x로 업그레이드 후 정확한 에러 메시지 확인: "IP belonging to a cloud provider"

**원인 2 — Webshare 무료 티어 = 데이터센터 IP**
Webshare 무료 플랜이 제공하는 프록시는 **Residential IP가 아닌 데이터센터 IP**.  
YouTube는 이 IP들도 이미 차단 목록에 보유 → 429 (Too Many Requests) 반복.

### 시도한 해결책과 결과

| 시도 | 결과 |
|------|------|
| youtube_transcript_api 0.6.3 → 1.2.4 업그레이드 | ❌ 여전히 IP 차단 (에러 메시지만 명확해짐) |
| Webshare 무료 프록시 (WebshareProxyConfig) | ❌ 데이터센터 IP라 429 동일 차단 |
| `proxies=` → `proxy_config=` 파라미터 수정 | ✅ 코드 오류 수정됨, 차단 문제는 별개 |

### 진단 과정

1. 로컬에서 동일 영상 자막 추출 → **성공** (일반 가정 IP)
2. Railway Console에서 직접 테스트 → **실패** (클라우드 IP 차단)
3. Webshare 적용 후 Console 재테스트 → **실패** (429, 데이터센터 IP 차단)

→ **문제는 코드가 아닌 Railway 서버 IP 자체**

### 결론 및 해결 방향

Railway(Google Cloud) 환경에서는 YouTube 자막 API를 정상 사용 불가.  
유료 Residential 프록시($5/월~) 없이는 Railway에서 해결 불가.

**채택한 해결책: Render.com으로 배포 플랫폼 이전**
- Render.com은 Google Cloud가 아닌 별도 인프라 사용
- 동일 Dockerfile 그대로 사용 가능 (`render.yaml` 추가만 필요)
- 무료 플랜 제공 (단, 15분 비활성 시 슬립)

### 교훈
- YouTube 자막 API는 클라우드 IP(GCP, AWS, Azure)에서 전면 차단됨
- Webshare 등 무료 프록시는 데이터센터 IP라 동일하게 차단
- 우회 방법: ① Residential 유료 프록시 ② 비-클라우드 플랫폼 이전 ③ 클라이언트(앱)에서 자막 추출
- 플랫폼 선택 시 "어떤 클라우드를 쓰는지" 확인 필요 (YouTube 우회 목적이면 GCP/AWS/Azure 제외)

---

## 🐛 이슈 #6 — Flutter APK 빌드 연속 실패 (4단계)

### 배경
Render.com 배포 + 클라이언트 자막 추출 아키텍처 완료 후 Flutter APK 빌드 시도.  
총 4가지 오류가 순차적으로 발생.

### 오류 1 — `summary_model.g.dart` 미생성

**증상**
```
lib/models/summary_model.dart:3:6: Error: Can't use 'lib/models/summary_model.g.dart' as a part, because it has no 'part of' declaration.
Method not found: '_$VideoMetadataFromJson'
```

**원인**  
`json_serializable` 코드 생성 파일(`*.g.dart`)이 없는 상태에서 빌드 시도.  
`flutter pub run build_runner build`를 한 번도 실행하지 않았음.

**해결**
```powershell
flutter pub run build_runner build --delete-conflicting-outputs
```

---

### 오류 2 — `DioExceptionType.connectionError` 누락

**증상**
```
lib/services/api_service.dart:107:19: Error: The type 'DioExceptionType' is not exhaustively matched by the switch cases since it doesn't match 'DioExceptionType.connectionError'.
```

**원인**  
`dio` 최신 버전(5.9.2)에서 `DioExceptionType.connectionError` 케이스가 추가됐는데 switch문에 없음.

**해결**  
`api_service.dart` switch문에 케이스 추가:
```dart
case DioExceptionType.connectionError:
  _logger.e('Connection error: ${error.message}');
```

---

### 오류 3 — Kotlin 증분 컴파일 크로스 드라이브 버그 (Windows)

**증상**
```
java.lang.IllegalArgumentException: this and base files have different roots:
C:\Users\82102\AppData\Local\Pub\Cache\...\shared_preferences_android\...
and D:\AI\260620_3_Multimedia_summary\frontend\android
```

**원인**  
Kotlin 증분 컴파일러가 캐시(C드라이브)와 프로젝트(D드라이브) 간 상대 경로 계산 불가.  
Windows에서 드라이브가 다르면 상대 경로가 성립되지 않음 (Linux/Mac에는 없는 문제).

**해결**  
`frontend/android/gradle.properties`에 추가:
```properties
kotlin.incremental=false
```

**부작용**: 매 빌드가 풀빌드로 돌아가 빌드 시간 증가 (~9분/회)

---

### 오류 4 — Gradle 인스턴스 Lock 충돌

**증상**
```
Timeout waiting to lock cache directory md-supplier (C:\Users\82102\.gradle\caches\8.12\md-supplier).
It is currently in use by another Gradle instance. Owner PID: 25584
```

**원인**  
이전 빌드를 bash `&` 백그라운드로 실행하여 프로세스가 살아있는 상태에서 새 빌드 시작.  
두 Gradle 인스턴스가 동일 캐시 디렉토리 lock 경합.

**해결**  
java 프로세스 전체 종료 + lock 파일 수동 삭제:
```powershell
Get-Process java | Stop-Process -Force
Remove-Item "$env:USERPROFILE\.gradle\caches\8.12\md-supplier\md-supplier.lock" -Force
```

### 교훈
- Windows 멀티 드라이브 환경(C:, D:)에서 Flutter 프로젝트는 `kotlin.incremental=false` 필수
- build_runner는 git clone 후, pubspec.yaml 의존성 변경 후 반드시 실행
- Gradle 백그라운드 빌드는 반드시 추적 가능한 방법으로 실행 (bash `&` 금지)

---

## 🐛 이슈 #7 — APK 설치 후 "요약생성 실패" 오류

### 증상
APK 설치 후 YouTube URL 입력 → "요약생성 실패" 즉시 표시.

### 원인 분석

**원인 1 — 자막 추출 실패 시 서버로 전송 (서버도 실패)**  
`home_screen.dart`가 자막 추출 실패 시 `transcript: null`로 서버 요청을 보내는 구조였음.  
서버는 transcript가 없으면 YouTube에서 직접 추출 시도 → IP 차단으로 500 에러.

```
서버 응답: {"detail":"Cannot extract transcript: YouTube is blocking requests from your IP..."}
```

**원인 2 — Claude API 응답 타임아웃**  
Flutter 앱 수신 타임아웃 = 30초. Claude API 요약은 60~120초 소요 가능.

### 해결

`home_screen.dart` — 자막 추출 실패 시 즉시 에러 표시:
```dart
// 변경 전: catch(e) 후 서버 전송 계속
// 변경 후:
} catch (e) {
    throw Exception('자막 추출 실패: 이 영상에 자막이 없거나 접근할 수 없습니다.\n($e)');
}
```

`api_service.dart` — 타임아웃 30초 → 180초:
```dart
static const Duration _receiveTimeout = Duration(seconds: 180);
```

### 교훈
- 클라이언트에서 자막 추출 실패 → 서버에도 전달할 것이 없음 → 즉시 에러 표시가 맞음
- Claude API 같이 처리 시간이 가변적인 경우 타임아웃은 충분히 넉넉하게 설정

---

## 🐛 이슈 #8 — youtube_explode_dart URL 파싱 실패 (youtu.be + ?si= 파라미터)

### 증상
`https://youtu.be/eImK97E4w20?si=UwhPIrSYanEjkUYt` 링크로 요약 시도 → "요약생성 실패 excep~" 즉시 표시.  
에러 다이얼로그 없이 3초 스낵바로만 표시되어 전체 메시지 확인 불가.

### 원인 분석

**원인 1 — VideoId(url) 에 전체 URL 전달**  
`youtube_explode_dart`의 `VideoId(videoUrl)` 생성자에 단축 URL + `?si=` 파라미터가 포함된 전체 URL을 전달.  
`?si=` 는 YouTube 공유 추적 파라미터로 라이브러리가 파싱 실패할 가능성 존재.

**원인 2 — 에러 메시지 3초 스낵바로 잘려서 디버깅 불가**  
오류 전체 텍스트를 볼 수 없어 정확한 원인 파악 불가.

### 해결

**해결 1 — 비디오 ID 직접 추출 후 전달** (`transcript_service.dart`):
```dart
String? _extractVideoId(String url) {
    final uri = Uri.tryParse(url);
    if (uri == null) return null;
    if (uri.host == 'youtu.be') return uri.pathSegments.firstOrNull; // youtu.be/ID
    return uri.queryParameters['v']; // youtube.com/watch?v=ID
}
// VideoId(rawId) — URL 대신 순수 ID만 전달
```

지원 URL 형식:
- `https://youtu.be/ID?si=xxx` → `ID`
- `https://youtube.com/watch?v=ID&t=30` → `ID`

**해결 2 — 에러 다이얼로그로 전체 내용 표시** (`home_screen.dart`):
```dart
showDialog(
    builder: (ctx) => AlertDialog(
        content: SingleChildScrollView(child: SelectableText(message)),
    ),
);
```

### 교훈
- `youtube_explode_dart`에 URL 전체를 넘기지 말고 비디오 ID만 추출해서 전달
- 에러 메시지는 스낵바(3초, 잘림) 대신 스크롤 가능한 다이얼로그로 표시해야 디버깅 가능
- 공유 URL에는 `?si=`, `&t=`, `&list=` 등 불필요한 파라미터가 포함될 수 있음 → 항상 파싱 필요

---

## 🐛 이슈 #9 — AndroidManifest.xml INTERNET 권한 누락

### 증상
```
ClientException with SocketException: Failed host lookup: 'www.youtube.com'
(OS Error: No address associated with hostname, errno = 7)
```
인터넷 자체 연결 불가. DNS 조회 실패.

### 원인
`AndroidManifest.xml`에 `<uses-permission android:name="android.permission.INTERNET" />` 누락.  
Flutter **debug 빌드**는 자동으로 INTERNET 권한을 추가하지만, **release 빌드**는 명시 필수.  
로컬 debug 테스트에서는 정상 → release APK에서만 네트워크 불가 → 원인 파악 지연됨.

### 해결
`frontend/android/app/src/main/AndroidManifest.xml` 상단에 추가:
```xml
<uses-permission android:name="android.permission.INTERNET" />
```

### 교훈
- Flutter release APK 만들 때 AndroidManifest.xml INTERNET 권한은 필수 체크 항목
- debug ↔ release 동작 차이: 네트워크, 권한, 서명, 난독화 등 다름
- 향후 새 Flutter 프로젝트 시작 시 즉시 추가할 것

---

## 🐛 이슈 #10 — youtube_explode_dart XmlParserException + Dio 자동 파싱 충돌

### 증상 1 (youtube_explode_dart 사용 시)
```
XmlParserException: Expected a single root element at 1:1
```
라이브러리 내부에서 YouTube 자막 응답을 XML로 파싱 실패.

### 원인 1
`youtube_explode_dart ^2.3.0`이 YouTube 최신 caption API 변경을 반영 못 함.  
YouTube caption 응답 형식이 바뀌었거나 라이브러리 파싱 로직이 오래됨.

### 해결 1
`youtube_explode_dart` 완전 제거 → Dio로 YouTube 페이지 직접 파싱.  
`ytInitialPlayerResponse`의 `captionTracks` 추출 → baseUrl로 JSON3 형식 자막 요청.

---

### 증상 2 (Dio 직접 파싱 시)
```
Exception: 자막 내용이 비어 있습니다.
```
자막 URL 가져오기는 성공했으나 파싱 결과가 빈 문자열.

### 원인 2
Dio의 기본 `responseType`이 JSON → 자막 응답을 자동으로 `Map`으로 파싱.  
이후 `captionResp.data is String` 체크 실패 → encode/decode 우회 경로로 들어가 구조 깨짐.

### 해결 2
```dart
Dio(BaseOptions(responseType: ResponseType.plain))  // 항상 String으로 받기
```
JSON3 파싱 실패 시 에러 메시지에 응답 앞부분 포함하여 다음 디버깅 지원.

### 교훈
- Dio는 Content-Type이 JSON이면 자동 파싱 → `responseType: ResponseType.plain` 명시 필요
- 외부 라이브러리(youtube_explode_dart)는 YouTube API 변경에 취약 → 직접 HTTP 구현이 더 안정적
- 디버깅 어려운 모바일 앱은 에러 메시지에 raw 응답 앞부분을 포함시켜야 빠르게 원인 파악 가능

---

## 🐛 이슈 #11 — YouTube 자막 추출 근본적 실패: 쿠키 세션 방식 한계

### 증상
```
Exception: 자막 응답이 비었습니다.
Exception: 이 영상에서 자막을 찾을 수 없습니다. (ko/en 수동 및 자동생성 자막 모두 없음)
```
cookie_jar + CookieManager로 YouTube 세션 유지해도 captionTracks baseUrl이 빈 응답 반환.

### 원인
YouTube caption URL(baseUrl)은 **인증된 브라우저 세션**이 필요.  
모바일 HTTP 클라이언트(Dio)는 브라우저의 실제 쿠키 스택(CONSENT, NID, VISITOR 등 수십 개)을  
완전히 재현 불가능. YouTube가 IP 기반 + 세션 검증으로 이중 차단.

시도한 방법 5가지 전부 실패:
1. youtube_explode_dart (XmlParserException — YouTube API 변경)
2. timedtext API (빈 응답)
3. 수동 쿠키 헤더 (빈 응답)
4. cookie_jar 자동 세션 관리 (빈 응답)
5. 다양한 User-Agent 위장 (빈 응답)

### 해결 — 아키텍처 전환
**Gemini API의 YouTube 네이티브 접근 활용**.  
Google/Gemini는 YouTube 소유사로 직접 영상 이해 가능 → 자막 추출 불필요.

```python
# backend/app/services/gemini_service.py
model = genai.GenerativeModel("models/gemini-2.5-flash")
response = model.generate_content([
    {"file_data": {"file_uri": youtube_url, "mime_type": "video/mp4"}},
    "이 YouTube 영상의 내용을 한국어로 상세하게 작성해주세요."
])
```

Flutter 앱은 이제 URL만 서버로 전송 — 자막 추출 코드 완전 제거.

### 결과
- `gemini-2.5-flash`로 YouTube 영상 완벽 요약 성공
- TranscriptService.dart 삭제, cookie_jar/dio_cookie_manager 의존성 제거
- 아키텍처 단순화: 앱 → URL 전송 → 서버 Gemini 처리 → Claude 분석 → 결과 반환

### 교훈
- YouTube 자막 추출은 실제 브라우저 없이는 불가능에 가까움
- "왜 안 되나" 보다 "다른 방법은 없나"로 발상 전환이 핵심
- Gemini(Google 계열) + YouTube = 네이티브 접근 가능 (다른 AI API는 불가)
- GEMINI_API_KEY는 Render 환경변수로만 관리 (.env 커밋 절대 금지)

---

## ✅ 변경 이력

| 날짜 | 버전 | 변경 내용 |
|------|------|-----------|
| 2026-06-20 | v0.01 | Railway Dockerfile 경로 오류 디버깅 및 해결 |
| 2026-06-20 | v0.01 | Railway 환경변수 미주입 + 앱 시작 실패 해결 |
| 2026-06-20 | v0.01 | Railway Public Domain 미생성으로 외부 접속 불가 해결 |
| 2026-06-20 | v0.01 | yt-dlp IP 차단 → oEmbed 전환, youtube_transcript_api 0.6.3→1.2.4 업그레이드 |
| 2026-06-21 | v0.01 | Railway(GCP) IP + Webshare 무료 프록시 모두 YouTube 차단 → Render.com 이전 결정 |
| 2026-06-21 | v0.01 | Flutter APK 빌드 4단계 오류 해결 (이슈 #6) |
| 2026-06-21 | v0.01 | APK "요약생성 실패" 원인 분석 및 수정 (이슈 #7) |
| 2026-06-21 | v0.01 | youtu.be URL 파싱 실패 + 에러 다이얼로그 개선 (이슈 #8) |
| 2026-06-21 | v0.01 | AndroidManifest INTERNET 권한 누락 → release APK 네트워크 불가 (이슈 #9) |
| 2026-06-21 | v0.01 | youtube_explode_dart 제거 + Dio responseType plain 강제 (이슈 #10) |
| 2026-06-21 | v0.01 | YouTube 자막 추출 5가지 방법 전부 실패 → Gemini API 아키텍처 전환 (이슈 #11) |

---

*다음 이슈 발생 시 이 파일에 ## 이슈 #11 로 추가*
