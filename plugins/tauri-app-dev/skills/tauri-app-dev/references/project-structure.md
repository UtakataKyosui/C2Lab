# Tauri v2 プロジェクト構造・tauri.conf.json 詳細

## 完全なプロジェクトレイアウト

```
my-tauri-app/
├── src/                          # フロントエンドソース（フレームワーク依存）
│   ├── main.ts                   # JSエントリポイント
│   ├── App.vue / App.tsx / App.svelte
│   └── ...
├── src-tauri/                    # Rust バックエンド
│   ├── src/
│   │   ├── lib.rs                # アプリのメインロジック（モバイル対応の場合エントリ）
│   │   └── main.rs               # デスクトップバイナリのエントリポイント
│   ├── capabilities/
│   │   └── default.json          # デフォルト capabilities（権限設定）
│   ├── icons/                    # アプリアイコン各サイズ
│   │   ├── 32x32.png
│   │   ├── 128x128.png
│   │   ├── icon.icns             # macOS
│   │   ├── icon.ico              # Windows
│   │   └── icon.png
│   ├── gen/                      # 自動生成ファイル（コミット不要）
│   │   └── schemas/              # capabilities JSON スキーマ
│   ├── Cargo.toml                # Rust 依存関係
│   ├── Cargo.lock                # ロックファイル（必ずコミットすること）
│   └── tauri.conf.json           # Tauri メイン設定
├── public/                       # 静的ファイル
├── dist/                         # フロントエンドビルド出力（gitignore推奨）
├── package.json
├── vite.config.ts / next.config.js / ...
└── .gitignore
```

## src-tauri/src/lib.rs（アプリエントリ）

```rust
// モバイル対応の場合は cfg_attr マクロが必要
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        // プラグインを登録
        .plugin(tauri_plugin_shell::init())
        // コマンドを登録
        .invoke_handler(tauri::generate_handler![
            greet,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}
```

## src-tauri/src/main.rs

```rust
// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    app_lib::run();
}
```

## tauri.conf.json 全設定項目

```json
{
  "$schema": "https://schema.tauri.app/config/2",

  "productName": "my-app",
  "version": "0.1.0",
  "identifier": "com.example.myapp",

  "build": {
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build",
    "devUrl": "http://localhost:5173",
    "frontendDist": "../dist"
  },

  "app": {
    "windows": [
      {
        "label": "main",
        "title": "My App",
        "width": 800,
        "height": 600,
        "resizable": true,
        "fullscreen": false,
        "decorations": true,
        "transparent": false,
        "center": true,
        "minWidth": 400,
        "minHeight": 300
      }
    ],
    "security": {
      "csp": null
    },
    "trayIcon": {
      "iconPath": "icons/32x32.png",
      "iconAsTemplate": true,
      "menuOnLeftClick": false,
      "title": "My App",
      "tooltip": "My App"
    }
  },

  "bundle": {
    "active": true,
    "targets": "all",
    "icon": [
      "icons/32x32.png",
      "icons/128x128.png",
      "icons/128x128@2x.png",
      "icons/icon.icns",
      "icons/icon.ico"
    ],
    "resources": {},
    "externalBin": [],
    "copyright": "",
    "category": "DeveloperTool",
    "shortDescription": "",
    "longDescription": "",
    "deb": {
      "depends": [],
      "desktopTemplate": null
    },
    "macOS": {
      "frameworks": [],
      "minimumSystemVersion": "10.13",
      "signingIdentity": null,
      "providerShortName": null,
      "entitlements": null
    },
    "windows": {
      "certificateThumbprint": null,
      "digestAlgorithm": "sha256",
      "timestampUrl": "",
      "webviewInstallMode": {
        "type": "embedBootstrapper"
      }
    },
    "iOS": {
      "developmentTeam": "YOUR_TEAM_ID"
    },
    "android": {
      "minSdkVersion": 24
    }
  }
}
```

## Cargo.toml の標準構成

```toml
[package]
name = "app"
version = "0.1.0"
description = "A Tauri App"
authors = []
edition = "2021"

# See more keys and their definitions at https://doc.rust-lang.org/cargo/reference/manifest.html

[lib]
# The `_name` for the lib target defaults to the package name, replacing -
# with _. Targets are required to have an explicit crate type.
#
# Selecting `staticlib` ensures that all Rust code, including Tauri, is
# compiled into a single library file for mobile.
# Selecting `cdylib` ensures that the library can be loaded by the Tauri
# mobile plugins.
crate-type = ["staticlib", "cdylib", "rlib"]

[build-dependencies]
tauri-build = { version = "2", features = [] }

[dependencies]
tauri = { version = "2", features = [] }
tauri-plugin-shell = "2"
serde = { version = "1", features = ["derive"] }
serde_json = "1"
```

## .gitignore の推奨設定

```
# Tauri
/src-tauri/target/
/src-tauri/gen/

# Frontend
/dist/
node_modules/
```

## ディレクトリ別役割まとめ

| ディレクトリ/ファイル | 役割 |
|---------------------|------|
| `src-tauri/src/lib.rs` | アプリのメインロジック、コマンド定義 |
| `src-tauri/src/main.rs` | デスクトップバイナリエントリ（通常変更不要） |
| `src-tauri/capabilities/` | 権限（capabilities）設定 JSON |
| `src-tauri/icons/` | アプリアイコン各サイズ |
| `src-tauri/gen/` | 自動生成（コミット不要、gitignore 推奨） |
| `src-tauri/tauri.conf.json` | Tauri 全設定（ウィンドウ/ビルド/バンドル） |
| `src-tauri/Cargo.lock` | **必ずコミットすること**（再現性） |
