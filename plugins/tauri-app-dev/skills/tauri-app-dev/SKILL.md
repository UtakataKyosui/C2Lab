---
name: Tauri App Development
description: This skill should be used when the user wants to build a Tauri v2 application, set up a new Tauri project, implement IPC communication with invoke/events/channels, configure tauri.conf.json, set up capabilities/permissions, develop for mobile (iOS/Android), integrate frontend frameworks (React/Vue/Svelte), use official Tauri plugins, or build and deploy a Tauri app. Covers the full Tauri v2 application development lifecycle.
version: 0.1.0
---

# Tauri v2 アプリケーション開発

## 概要

Tauri v2 はマルチプロセスアーキテクチャを採用したクロスプラットフォームアプリフレームワーク。

- **WebView プロセス**: フロントエンド（HTML/CSS/JS）を描画
- **Core プロセス**: Rust バックエンド、システム API へのアクセス
- **プロセス間通信**: IPC（invoke / events / channels）

対応プラットフォーム: **Windows, macOS, Linux, iOS, Android**

## 新規プロジェクトのセットアップ

### create-tauri-app（推奨）

```bash
npm create tauri-app@latest
# または
cargo install create-tauri-app && create-tauri-app
```

プロンプトでフロントエンドフレームワークを選択（React / Vue / Svelte / Vanilla など）。

### 既存フロントエンドへの追加

```bash
cd my-frontend-project
npm install --save-dev @tauri-apps/cli
npx tauri init
```

### プロジェクト構造

```
my-app/
├── src/                    # フロントエンドソース
├── src-tauri/
│   ├── src/
│   │   ├── lib.rs          # アプリエントリポイント
│   │   └── main.rs         # バイナリエントリ
│   ├── capabilities/
│   │   └── default.json    # 権限設定
│   ├── icons/              # アプリアイコン
│   ├── Cargo.toml
│   └── tauri.conf.json     # Tauri 設定
├── package.json
└── ...
```

詳細: `references/project-structure.md`

## IPC 通信パターン

### invoke（コマンド呼び出し）

**Rust 側（src-tauri/src/lib.rs）**:
```rust
use tauri::command;

#[command]
async fn greet(name: String) -> String {
    format!("Hello, {}!", name)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![greet])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

**TypeScript 側**:
```typescript
import { invoke } from '@tauri-apps/api/core';

const message = await invoke<string>('greet', { name: 'World' });
```

### イベント（双方向通信）

```typescript
// フロントエンドでイベントをリッスン
import { listen } from '@tauri-apps/api/event';

const unlisten = await listen<string>('my-event', (event) => {
  console.log(event.payload);
});

// クリーンアップ
unlisten();
```

```rust
// Rust 側からイベントを発火
use tauri::Emitter;

app.emit("my-event", "payload data").unwrap();
```

詳細: `references/ipc-patterns.md`

## セキュリティモデル

Tauri v2 は **capabilities** による明示的な権限管理を採用。

### capabilities/default.json の基本構造

```json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "default",
  "description": "Default capabilities",
  "windows": ["main"],
  "permissions": [
    "core:default",
    "shell:allow-open",
    "fs:allow-read-text-file"
  ]
}
```

- `identifier`: capabilities の一意な識別子（必須）
- `windows`: どのウィンドウに適用するか
- `permissions`: 許可する権限のリスト

詳細: `references/security-capabilities.md`

## フロントエンド統合

### tauri.conf.json の devUrl 設定

```json
{
  "build": {
    "beforeDevCommand": "npm run dev",
    "beforeBuildCommand": "npm run build",
    "devUrl": "http://localhost:5173",
    "frontendDist": "../dist"
  }
}
```

フレームワーク別の設定: `references/frontend-integration.md`

## 開発コマンド

```bash
# 開発サーバー起動（ホットリロード有効）
npm run tauri dev
# または
cargo tauri dev

# プロダクションビルド
npm run tauri build
# または
cargo tauri build
```

## 公式プラグインの利用

Tauri v2 には 40 以上の公式プラグインがある。

### インストール例（fs プラグイン）

```bash
# Rust 依存関係
cargo add tauri-plugin-fs

# npm パッケージ
npm install @tauri-apps/plugin-fs
```

```rust
// src-tauri/src/lib.rs に登録
tauri::Builder::default()
    .plugin(tauri_plugin_fs::init())
    // ...
```

```typescript
// フロントエンドで使用
import { readTextFile, BaseDirectory } from '@tauri-apps/plugin-fs';

const content = await readTextFile('config.json', {
  baseDir: BaseDirectory.AppConfig,
});
```

主要プラグイン一覧: `references/official-plugins.md`

## モバイル開発

### セットアップ

```bash
# iOS（macOS が必要）
npm run tauri ios init
npm run tauri ios dev

# Android
npm run tauri android init
npm run tauri android dev
```

### モバイル向け設定

```json
{
  "bundle": {
    "iOS": {
      "developmentTeam": "YOUR_TEAM_ID"
    },
    "android": {
      "minSdkVersion": 24
    }
  }
}
```

詳細: `references/mobile-development.md`

## ビルドとデプロイ

```bash
# デスクトップビルド（インストーラー生成）
npm run tauri build

# 出力先
# src-tauri/target/release/bundle/
```

**重要**: `Cargo.lock` はコミットすること（再現性のため）。

詳細: `references/build-deploy.md`

## 参考ファイル

- **`references/project-structure.md`** - プロジェクト構成・tauri.conf.json 全設定項目
- **`references/ipc-patterns.md`** - invoke/events/channels の実装例（Rust + TypeScript）
- **`references/security-capabilities.md`** - capabilities JSON・CSP 設定・権限一覧
- **`references/mobile-development.md`** - iOS/Android 開発・TAURI_DEV_HOST 設定
- **`references/frontend-integration.md`** - React/Vue/Svelte 統合・beforeDevCommand
- **`references/official-plugins.md`** - 公式プラグイン 40+ 一覧・インストール方法
- **`references/build-deploy.md`** - ビルド・クロスコンパイル・デプロイ
