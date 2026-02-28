# Tauri v2 モバイル開発（iOS / Android）

## 前提条件

### iOS（macOS 専用）
- macOS 12+ が必要
- Xcode 14+
- iOS 16+ シミュレーターまたは実機
- Apple Developer アカウント（実機テスト時）

```bash
# 必要ツールのインストール
xcode-select --install
rustup target add aarch64-apple-ios x86_64-apple-ios aarch64-apple-ios-sim
```

### Android
- Android Studio
- Android SDK（API Level 24+）
- NDK

```bash
# Android ターゲット追加
rustup target add aarch64-linux-android armv7-linux-androideabi i686-linux-android x86_64-linux-android

# 環境変数設定（~/.bashrc または ~/.zshrc）
export JAVA_HOME=/path/to/java
export ANDROID_HOME=/path/to/android-sdk
export NDK_HOME="$ANDROID_HOME/ndk/$(ls -1 $ANDROID_HOME/ndk)"
```

## プロジェクトのモバイル初期化

```bash
# iOS プロジェクトを初期化
npm run tauri ios init
# または
cargo tauri ios init

# Android プロジェクトを初期化
npm run tauri android init
# または
cargo tauri android init
```

これで `src-tauri/gen/` 以下にネイティブプロジェクトが生成される:
```
src-tauri/gen/
├── android/              # Android Gradle プロジェクト
│   ├── app/
│   │   └── src/main/
│   │       ├── AndroidManifest.xml
│   │       └── kotlin/com/example/myapp/
└── apple/               # Xcode プロジェクト
    └── MyApp.xcodeproj/
```

## 開発（ホットリロード）

### iOS シミュレーター

```bash
npm run tauri ios dev
# または
cargo tauri ios dev
```

### iOS 実機

```bash
# デバイスを接続後
cargo tauri ios dev --device "iPhone 15 Pro"
```

### Android エミュレーター

```bash
npm run tauri android dev
# または
cargo tauri android dev
```

### Android 実機（ネットワーク経由）

実機は PC のローカルサーバーにアクセスできないため、環境変数の設定が必要:

```bash
# PC の LAN IP アドレスを確認
ip addr show | grep "inet " | grep -v 127.0.0.1

# 環境変数を設定してから開発サーバー起動
TAURI_DEV_HOST=192.168.1.100 npm run tauri android dev
```

`tauri.conf.json` では `devUrl` を自動的に `http://192.168.1.100:5173` に書き換える。

## Rust コードのモバイル対応

### lib.rs のモバイルエントリポイント

```rust
// #[cfg_attr(mobile, tauri::mobile_entry_point)] が必須
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            greet,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

### プラットフォーム別コード分岐

```rust
#[tauri::command]
async fn get_platform_info() -> String {
    #[cfg(target_os = "android")]
    return "android".to_string();

    #[cfg(target_os = "ios")]
    return "ios".to_string();

    #[cfg(not(mobile))]
    return "desktop".to_string();
}

// cfg_attr によるプラットフォーム別属性
#[cfg(target_os = "android")]
fn setup_android_notifications() {
    // Android 固有の処理
}
```

### デスクトップ/モバイル分岐モジュール

```rust
// src/lib.rs

#[cfg(desktop)]
mod desktop;
#[cfg(mobile)]
mod mobile;

#[cfg(desktop)]
use desktop::PlatformImpl;
#[cfg(mobile)]
use mobile::PlatformImpl;
```

## tauri.conf.json のモバイル設定

```json
{
  "bundle": {
    "iOS": {
      "developmentTeam": "ABCD1234EF",
      "minimumSystemVersion": "16.0",
      "frameworks": [],
      "exceptionDomain": {},
      "entitlements": null
    },
    "android": {
      "minSdkVersion": 24,
      "versionCode": 1
    }
  },
  "app": {
    "windows": [
      {
        "label": "main",
        "title": "My App",
        "width": 390,
        "height": 844,
        "fullscreen": false
      }
    ]
  }
}
```

## capabilities のモバイル対応

```json
{
  "$schema": "../gen/schemas/mobile-schema.json",
  "identifier": "mobile-default",
  "platforms": ["android", "ios"],
  "windows": ["main"],
  "permissions": [
    "core:default",
    "notification:default",
    "http:default"
  ]
}
```

### プラットフォーム別スキーマの切り替え

### デスクトップ用

```json
{
  "$schema": "../gen/schemas/desktop-schema.json"
}
```

### モバイル用

```json
{
  "$schema": "../gen/schemas/mobile-schema.json"
}
```

## モバイルでのネイティブ機能

### カメラ（公式プラグインなし → サードパーティまたはカスタム）

モバイル固有のネイティブ機能には、カスタム Tauri プラグインを作成する必要がある場合がある。

### geolocation（位置情報）

```bash
cargo add tauri-plugin-geolocation
npm install @tauri-apps/plugin-geolocation
```

```json
// capabilities/mobile.json
{
  "permissions": [
    "geolocation:allow-get-current-position",
    "geolocation:allow-request-permissions"
  ]
}
```

```typescript
import { getCurrentPosition, requestPermissions } from '@tauri-apps/plugin-geolocation';

const permissions = await requestPermissions(['location']);
const position = await getCurrentPosition();
console.log(position.coords.latitude, position.coords.longitude);
```

### biometric（生体認証）

```bash
cargo add tauri-plugin-biometric
npm install @tauri-apps/plugin-biometric
```

```typescript
import { authenticate, checkStatus } from '@tauri-apps/plugin-biometric';

const status = await checkStatus();
if (status.isAvailable) {
  await authenticate('Authenticate to access your data');
}
```

## ビルド（本番）

```bash
# iOS アーカイブ（App Store 提出用）
cargo tauri ios build

# Android APK / AAB
cargo tauri android build

# 特定のターゲット指定
cargo tauri android build --target aarch64
```

## よくある問題と解決策

### TAURI_DEV_HOST が必要なケース

Android 実機で `net::ERR_CONNECTION_REFUSED` が出る場合:
```bash
# PC の IP を確認（192.168.x.x 形式）
ip addr show wlan0

TAURI_DEV_HOST=192.168.1.100 cargo tauri android dev
```

### iOS シミュレーターが起動しない

```bash
# シミュレーター一覧確認
xcrun simctl list devices available

# 特定のシミュレーターを指定
cargo tauri ios dev --device "iPhone 16"
```

### Android: SDK ライセンス未承認

```bash
# SDK ライセンスに同意
$ANDROID_HOME/tools/bin/sdkmanager --licenses
```

### Rust のモバイルコンパイルエラー

モバイルは `std::process::exit` が使えないなど制限がある:
```rust
// 代わりに panic を使う
panic!("Fatal error: {}", msg);

// または tauri の終了 API を使う
app.exit(0);
```

## デバッグ

### Android ログ確認

```bash
# adb logcat でログを確認
adb logcat -s RustStdoutStderr

# または
adb logcat | grep "my-app"
```

### iOS ログ確認

Xcode のコンソールウィンドウ、または:
```bash
# idb を使用
idb log --udid <device-udid>
```
