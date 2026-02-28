# Tauri v2 セキュリティモデル・capabilities 詳細

## 概要

Tauri v2 はセキュリティを中心に設計されており、**capabilities** システムによって各ウィンドウが使用できる API を厳密に制御する。

## capabilities ファイルの配置

```
src-tauri/
└── capabilities/
    ├── default.json       # デフォルト権限
    ├── mobile.json        # モバイル専用権限（任意）
    └── desktop.json       # デスクトップ専用権限（任意）
```

## capabilities JSON の完全な構造

```json
{
  "$schema": "../gen/schemas/desktop-schema.json",
  "identifier": "default",
  "description": "Default permissions for the app",
  "local": true,
  "windows": ["main"],
  "permissions": [
    "core:default",
    "fs:allow-read-text-file",
    "fs:allow-write-text-file",
    "fs:allow-read-dir",
    "shell:allow-open",
    "dialog:allow-open",
    "dialog:allow-save",
    "notification:default"
  ]
}
```

### フィールド説明

| フィールド | 型 | 必須 | 説明 |
|-----------|---|------|------|
| `identifier` | string | **必須** | capabilities の一意な識別子 |
| `description` | string | 任意 | 説明文 |
| `local` | boolean | 任意 | `true` でローカルのみ（デフォルト: false） |
| `windows` | string[] | 任意 | 適用するウィンドウラベルのリスト |
| `permissions` | string[] | 任意 | 許可する権限のリスト |
| `platforms` | string[] | 任意 | 対象プラットフォーム（`"linux"/"macos"/"windows"/"android"/"ios"`） |

## 権限の命名規則

```
<plugin-name>:<permission-set-or-command>
```

例:
- `fs:allow-read-text-file` → fs プラグインの readTextFile を許可
- `fs:default` → fs プラグインのデフォルト権限セット
- `core:default` → Tauri コアのデフォルト権限

## プラットフォーム別 capabilities

```json
{
  "identifier": "mobile-only",
  "platforms": ["android", "ios"],
  "windows": ["main"],
  "permissions": [
    "geolocation:allow-get-current-position"
  ]
}
```

## 主要プラグインの権限一覧

### core（Tauri コア）

```
core:default                    # 基本コア機能
core:app:default                # アプリ情報
core:event:default              # イベントシステム
core:path:default               # パス解決
core:window:default             # ウィンドウ操作
core:webview:default            # WebView 操作
```

### fs（ファイルシステム）

```
fs:default                      # デフォルト（読み書き制限あり）
fs:allow-read-text-file         # テキストファイル読み取り
fs:allow-write-text-file        # テキストファイル書き込み
fs:allow-read-file              # バイナリファイル読み取り
fs:allow-write-file             # バイナリファイル書き込み
fs:allow-read-dir               # ディレクトリ一覧
fs:allow-create-dir             # ディレクトリ作成
fs:allow-remove-file            # ファイル削除
fs:allow-remove-dir             # ディレクトリ削除
fs:allow-rename                 # ファイル名変更
fs:allow-copy-file              # ファイルコピー
fs:allow-exists                 # ファイル存在確認
fs:allow-metadata               # メタデータ取得
fs:allow-watch                  # ファイル変更監視
```

### shell

```
shell:allow-open               # URL/ファイルをデフォルトアプリで開く
shell:allow-execute            # シェルコマンド実行（スコープ定義が必要）
```

### dialog

```
dialog:allow-open              # ファイル選択ダイアログ
dialog:allow-save              # ファイル保存ダイアログ
dialog:allow-message           # メッセージダイアログ
dialog:allow-ask               # 確認ダイアログ
dialog:allow-confirm           # 確認ダイアログ
```

### http

```
http:default                   # デフォルト（スコープ設定推奨）
http:allow-fetch               # HTTP リクエスト
```

### notification

```
notification:default           # デフォルト通知権限
notification:allow-send-notification  # 通知送信
notification:allow-check-permission   # 権限確認
notification:allow-request-permission # 権限要求
```

### store（永続化）

```
store:allow-get                # 値の取得
store:allow-set                # 値の設定
store:allow-delete             # 値の削除
store:allow-clear              # ストア全削除
store:allow-reset              # デフォルト値にリセット
store:allow-save               # ディスクに保存
store:allow-load               # ディスクから読み込み
```

### clipboard-manager

```
clipboard-manager:allow-read-text   # テキスト読み取り
clipboard-manager:allow-write-text  # テキスト書き込み
```

### os（OS 情報）

```
os:default                     # OS 情報取得
os:allow-platform              # プラットフォーム名
os:allow-version               # OS バージョン
os:allow-type                  # OS タイプ
```

### process

```
process:allow-exit             # アプリ終了
process:allow-restart          # アプリ再起動
```

### updater

```
updater:default                # 更新チェック・適用
updater:allow-check            # 更新チェック
updater:allow-download-and-install  # ダウンロード・インストール
```

## スコープ付き権限

一部の権限はスコープ（アクセス範囲制限）を設定する必要がある。

### ファイルシステムのスコープ

```json
{
  "identifier": "default",
  "windows": ["main"],
  "permissions": [
    {
      "identifier": "fs:allow-read-text-file",
      "allow": [
        { "path": "$APP_CONFIG_DIR/**" },
        { "path": "$APP_DATA_DIR/**" }
      ],
      "deny": [
        { "path": "$HOME/**" }
      ]
    }
  ]
}
```

利用可能なパス変数:
- `$HOME` - ホームディレクトリ
- `$APP_CONFIG_DIR` - アプリ設定ディレクトリ
- `$APP_DATA_DIR` - アプリデータディレクトリ
- `$APP_CACHE_DIR` - アプリキャッシュ
- `$DOWNLOAD_DIR` - ダウンロードフォルダ
- `$DOCUMENT_DIR` - ドキュメントフォルダ
- `$DESKTOP_DIR` - デスクトップ
- `$PICTURE_DIR` - ピクチャフォルダ

### HTTP のスコープ

```json
{
  "permissions": [
    {
      "identifier": "http:default",
      "allow": [
        { "url": "https://api.example.com/**" }
      ]
    }
  ]
}
```

## CSP（Content Security Policy）

`tauri.conf.json` の `app.security.csp` で設定:

```json
{
  "app": {
    "security": {
      "csp": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; connect-src 'self' https://api.example.com"
    }
  }
}
```

**開発中（CSP 無効）**:
```json
{
  "app": {
    "security": {
      "csp": null
    }
  }
}
```

## よくあるエラーと解決策

| エラー | 原因 | 解決策 |
|--------|------|--------|
| `Not allowed by scope` | capabilities に権限なし | 該当の `allow-*` を追加 |
| `Permission denied` | スコープ外のパス | `allow` にパスを追加 |
| CSP エラー | CSP でブロック | `connect-src` / `img-src` を追加 |
| `window is not defined in capabilities` | ウィンドウラベルが一致しない | `windows` フィールドを確認 |

## カスタムコマンドの permissions 設定

自分で定義したコマンドには capabilities への追加が不要（デフォルトで許可）。ただし、プラグインコマンドには明示的な権限追加が必要。
