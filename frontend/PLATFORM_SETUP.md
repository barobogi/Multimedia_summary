# Flutter 플랫폼 설정 가이드

## Android 설정

### 1. Intent 필터 설정

`android/app/src/main/AndroidManifest.xml`에 다음을 추가:

```xml
<activity
    android:name=".MainActivity"
    android:exported="true">
    <intent-filter>
        <action android:name="android.intent.action.MAIN" />
        <category android:name="android.intent.category.LAUNCHER" />
    </intent-filter>

    <!-- 공유 Intent 필터 추가 -->
    <intent-filter>
        <action android:name="android.intent.action.SEND" />
        <category android:name="android.intent.category.DEFAULT" />
        <data android:mimeType="text/plain" />
    </intent-filter>
</activity>
```

### 2. 권한 설정

`android/app/src/main/AndroidManifest.xml`에 필수 권한 추가:

```xml
<uses-permission android:name="android.permission.INTERNET" />
<uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />
<uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
```

### 3. build.gradle 설정

`android/app/build.gradle`:

```gradle
android {
    compileSdkVersion 34
    
    defaultConfig {
        applicationId "com.barobogi.multimedia_summary"
        minSdkVersion 21
        targetSdkVersion 34
        versionCode 1
        versionName "1.0.0"
    }
    
    signingConfigs {
        release {
            storeFile file("key.jks")
            storePassword System.getenv("KEYSTORE_PASSWORD")
            keyAlias System.getenv("KEY_ALIAS")
            keyPassword System.getenv("KEY_PASSWORD")
        }
    }
    
    buildTypes {
        release {
            signingConfig signingConfigs.release
        }
    }
}
```

### 4. Release APK 서명

```bash
# 키스토어 생성 (처음 한 번)
keytool -genkey -v -keystore key.jks \
    -keyalg RSA -keysize 2048 -validity 10000 \
    -alias multimedia-key

# 환경 변수 설정 (또는 gradle.properties)
export KEYSTORE_PASSWORD=your_password
export KEY_ALIAS=multimedia-key
export KEY_PASSWORD=your_key_password

# Release APK 빌드
flutter build apk --release
```

## iOS 설정

### 1. Info.plist 설정

`ios/Runner/Info.plist`에 다음 추가:

```xml
<key>NSLocalNetworkUsageDescription</key>
<string>이 앱은 동영상 요약을 위해 네트워크 접근이 필요합니다</string>

<key>NSBonjourServiceTypes</key>
<array>
    <string>_http._tcp</string>
    <string>_https._tcp</string>
</array>

<!-- 공유 확장 -->
<key>CFBundleURLTypes</key>
<array>
    <dict>
        <key>CFBundleURLSchemes</key>
        <array>
            <string>multimedia-summary</string>
        </array>
    </dict>
</array>
```

### 2. Podfile 설정

`ios/Podfile`:

```ruby
post_install do |installer|
  installer.pods_project.targets.each do |target|
    target.build_configurations.each do |config|
      config.build_settings['GCC_PREPROCESSOR_DEFINITIONS'] ||= [
        '$(inherited)',
        'PERMISSION_CAMERA=1',
      ]
    end
  end
end
```

### 3. Release 빌드

```bash
# iOS Pod 의존성 설치
cd ios
pod repo update
cd ..

# Release 빌드
flutter build ios --release

# 또는 Xcode로 배포
open ios/Runner.xcworkspace
```

## 공유 Intent 수신 처리

### Dart 코드 (main.dart)

```dart
import 'package:receive_sharing_intent/receive_sharing_intent.dart';

void main() {
  // 공유 Intent 수신 리스너 설정
  _handleSharedFiles();
  runApp(const MultimediaSummaryApp());
}

void _handleSharedFiles() {
  // 앱이 실행 중일 때 공유 받기
  ReceiveSharingIntent.instance.getMediaStream().listen(
    (List<SharedMediaFile> value) {
      if (value.isNotEmpty) {
        // 파일 또는 텍스트 처리
        for (var file in value) {
          if (file.type == SharedMediaType.text) {
            // 텍스트 (URL) 처리
            print('Received text: ${file.path}');
          }
        }
      }
    },
    onError: (err) {
      print('Error receiving sharing intent: $err');
    },
  );

  // 앱 시작 시 공유 Intent 처리
  ReceiveSharingIntent.instance.getInitialMedia().then(
    (List<SharedMediaFile> value) {
      if (value.isNotEmpty) {
        // 초기 공유 Intent 처리
      }
    },
  );
}
```

## 앱 설정

### android/app/build.gradle

```gradle
dependencies {
    // ... 기타 의존성 ...
    
    // 공유 Intent 수신
    implementation 'androidx.core:core:1.10.0'
}
```

### pubspec.yaml

```yaml
dependencies:
  # ... 기타 의존성 ...
  receive_sharing_intent: ^1.4.5
```

## 테스트

### Android 에뮬레이터에서 테스트

```bash
# 앱 실행
flutter run

# 다른 터미널에서 Intent 시뮬레이션
adb shell am start -a android.intent.action.SEND \
    --es android.intent.extra.TEXT "https://www.youtube.com/watch?v=..." \
    -t "text/plain" com.barobogi.multimedia_summary/.MainActivity
```

### 실기기 테스트

1. 기기에 앱 설치
2. YouTube 또는 다른 앱에서 공유하기
3. Multimedia Summary 앱 선택
4. 링크가 자동으로 입력되는지 확인

## 배포

### Google Play Store

1. Firebase 프로젝트 설정
2. 앱 서명 설정 (위 참고)
3. Release APK 생성
4. Google Play Console에 업로드
5. 메타데이터 및 권한 검토

### TestFlight (iOS)

1. Apple Developer 계정 필요
2. Xcode에서 Signing & Capabilities 설정
3. Archive 생성 후 App Store Connect 업로드
4. TestFlight 베타 테스팅 활성화

## 문제 해결

### Android Intent 받지 못함

- AndroidManifest.xml 문법 확인
- intent-filter 올바른 위치 확인 (activity 내부)
- `flutter clean && flutter run` 재실행

### iOS 공유 안 됨

- Info.plist 문법 확인
- 앱 번들 ID 일치 확인
- Xcode 캐시 정리: `flutter clean`

### APK 서명 오류

- 키스토어 비밀번호 확인
- Key Alias 확인
- 환경 변수 또는 gradle.properties 설정 확인

## 참고

- [Flutter Android 문서](https://flutter.dev/docs/deployment/android)
- [Flutter iOS 문서](https://flutter.dev/docs/deployment/ios)
- [Android Intent Filters](https://developer.android.com/guide/components/intents-filters)
- [iOS URLSchemes](https://developer.apple.com/documentation/uikit/inter-process_communication)
