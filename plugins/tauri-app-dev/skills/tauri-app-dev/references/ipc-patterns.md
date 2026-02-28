# Tauri v2 IPC パターン詳細

## IPC の3つの方式

| 方式 | 用途 | 方向 |
|------|------|------|
| `invoke` | コマンド呼び出し（単発リクエスト/レスポンス） | フロント → Rust → フロント |
| `events` | イベント通知 | 双方向 |
| `channels` | ストリーミング・進捗報告 | Rust → フロント（多対1） |

---

## 1. invoke（コマンド呼び出し）

### 基本パターン

**Rust（コマンド定義）**:
```rust
use tauri::command;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
pub struct CreateUserRequest {
    name: String,
    email: String,
}

#[derive(Serialize)]
pub struct User {
    id: u64,
    name: String,
    email: String,
}

// 非同期コマンド（推奨）
#[command]
pub async fn create_user(request: CreateUserRequest) -> Result<User, String> {
    // 実装
    Ok(User {
        id: 1,
        name: request.name,
        email: request.email,
    })
}

// 同期コマンド
#[command]
pub fn get_version() -> String {
    env!("CARGO_PKG_VERSION").to_string()
}
```

**登録（lib.rs）**:
```rust
#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![
            create_user,
            get_version,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

**TypeScript（呼び出し）**:
```typescript
import { invoke } from '@tauri-apps/api/core';

interface CreateUserRequest {
  name: string;
  email: string;
}

interface User {
  id: number;
  name: string;
  email: string;
}

// コマンド呼び出し
const user = await invoke<User>('create_user', {
  request: { name: 'Alice', email: 'alice@example.com' }
});

// 引数なし
const version = await invoke<string>('get_version');
```

### AppHandle を使うコマンド

```rust
use tauri::{command, AppHandle, Runtime};

#[command]
pub async fn open_window<R: Runtime>(app: AppHandle<R>) -> Result<(), String> {
    tauri::WebviewWindowBuilder::new(
        &app,
        "settings",
        tauri::WebviewUrl::App("/settings".into()),
    )
    .title("Settings")
    .build()
    .map_err(|e| e.to_string())?;
    Ok(())
}
```

### State（状態管理）付きコマンド

```rust
use tauri::{command, State};
use std::sync::Mutex;

pub struct AppState {
    pub counter: Mutex<u64>,
}

#[command]
pub fn increment(state: State<'_, AppState>) -> u64 {
    let mut counter = state.counter.lock().unwrap();
    *counter += 1;
    *counter
}

// lib.rs でステートを登録
pub fn run() {
    tauri::Builder::default()
        .manage(AppState { counter: Mutex::new(0) })
        .invoke_handler(tauri::generate_handler![increment])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
```

---

## 2. Events（イベント通知）

### Rust → フロントエンド

```rust
use tauri::{AppHandle, Emitter, Runtime};

// グローバルイベント（全ウィンドウに送信）
pub fn emit_progress<R: Runtime>(app: &AppHandle<R>, progress: u32) {
    app.emit("download-progress", progress).unwrap();
}

// 特定ウィンドウへのイベント
pub fn emit_to_main<R: Runtime>(app: &AppHandle<R>, message: &str) {
    app.emit_to("main", "notification", message).unwrap();
}
```

**TypeScript（受信）**:
```typescript
import { listen, once } from '@tauri-apps/api/event';

// 継続的にリッスン
const unlisten = await listen<number>('download-progress', (event) => {
  console.log(`Progress: ${event.payload}%`);
  console.log(`Source window: ${event.windowLabel}`);
});

// 一度だけ受信
await once<string>('notification', (event) => {
  alert(event.payload);
});

// クリーンアップ（コンポーネントのアンマウント時など）
unlisten();
```

### フロントエンド → Rust

```typescript
import { emit } from '@tauri-apps/api/event';

// フロントエンドからイベントを発火
await emit('user-action', { type: 'click', target: 'button' });
```

```rust
// Rust でフロントエンドからのイベントをリッスン
use tauri::Listener;

app.listen("user-action", |event| {
    println!("Received: {:?}", event.payload());
});
```

---

## 3. Channels（ストリーミング）

大量データや長時間処理の進捗報告に最適。

**Rust**:
```rust
use tauri::{command, ipc::Channel};
use serde::Serialize;

#[derive(Clone, Serialize)]
#[serde(rename_all = "camelCase", tag = "event", content = "data")]
pub enum DownloadEvent {
    #[serde(rename_all = "camelCase")]
    Started { url: String, content_length: u64 },
    #[serde(rename_all = "camelCase")]
    Progress { downloaded: u64, total: u64 },
    Finished,
    Error { message: String },
}

#[command]
pub async fn download_file(
    url: String,
    on_event: Channel<DownloadEvent>,
) -> Result<(), String> {
    on_event.send(DownloadEvent::Started {
        url: url.clone(),
        content_length: 1000,
    }).unwrap();

    // 処理中...
    for i in 0..=100 {
        on_event.send(DownloadEvent::Progress {
            downloaded: i * 10,
            total: 1000,
        }).unwrap();
        tokio::time::sleep(tokio::time::Duration::from_millis(50)).await;
    }

    on_event.send(DownloadEvent::Finished).unwrap();
    Ok(())
}
```

**TypeScript**:
```typescript
import { invoke, Channel } from '@tauri-apps/api/core';

type DownloadEvent =
  | { event: 'started'; data: { url: string; contentLength: number } }
  | { event: 'progress'; data: { downloaded: number; total: number } }
  | { event: 'finished' }
  | { event: 'error'; data: { message: string } };

const onEvent = new Channel<DownloadEvent>();

onEvent.onmessage = (message) => {
  switch (message.event) {
    case 'started':
      console.log(`Downloading ${message.data.url}`);
      break;
    case 'progress':
      const pct = (message.data.downloaded / message.data.total) * 100;
      updateProgressBar(pct);
      break;
    case 'finished':
      console.log('Download complete!');
      break;
    case 'error':
      console.error(message.data.message);
      break;
  }
};

await invoke('download_file', { url: 'https://example.com/file.zip', onEvent });
```

---

## エラーハンドリングのベストプラクティス

```rust
use serde::{Serialize, Deserialize};
use thiserror::Error;

#[derive(Debug, Error, Serialize)]
pub enum AppError {
    #[error("File not found: {0}")]
    FileNotFound(String),
    #[error("Permission denied")]
    PermissionDenied,
    #[error(transparent)]
    Io(#[from] std::io::Error),
}

// Tauri が自動的に Error を JSON に変換するため Serialize が必要
#[command]
pub async fn read_config(path: String) -> Result<String, AppError> {
    std::fs::read_to_string(&path).map_err(|_| AppError::FileNotFound(path))
}
```

**TypeScript**:
```typescript
try {
  const config = await invoke<string>('read_config', { path: '/config.json' });
} catch (error) {
  // error は Rust の AppError の Serialize 結果（文字列または JSON）
  console.error('Failed:', error);
}
```

---

## serde のフィールド名変換

Rust は snake_case、TypeScript は camelCase を使うため、`serde` で変換する。

```rust
#[derive(Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct FileInfo {
    file_name: String,      // TS側: fileName
    file_size: u64,         // TS側: fileSize
    last_modified: u64,     // TS側: lastModified
    is_directory: bool,     // TS側: isDirectory
}
```

**TypeScript インターフェース**:
```typescript
interface FileInfo {
  fileName: string;
  fileSize: number;
  lastModified: number;
  isDirectory: boolean;
}
```
