# Tauri v2 公式プラグイン一覧・使い方

すべての公式プラグインは `https://github.com/tauri-apps/plugins-workspace` で管理されている。

## インストールの共通手順

```bash
# Rust 依存関係
cargo add tauri-plugin-<name>

# npm パッケージ（フロントエンド API が必要な場合）
npm install @tauri-apps/plugin-<name>
```

```rust
// src-tauri/src/lib.rs に登録
tauri::Builder::default()
    .plugin(tauri_plugin_<name>::init())
    // ...
```

---

## ファイル・ストレージ系

### fs（ファイルシステム）

```bash
cargo add tauri-plugin-fs
npm install @tauri-apps/plugin-fs
```

```json
// capabilities/default.json
{
  "permissions": ["fs:default", "fs:allow-read-text-file", "fs:allow-write-text-file"]
}
```

```typescript
import {
  readTextFile,
  writeTextFile,
  readDir,
  mkdir,
  remove,
  exists,
  BaseDirectory,
} from '@tauri-apps/plugin-fs';

// テキストファイル読み取り
const content = await readTextFile('config.json', {
  baseDir: BaseDirectory.AppConfig,
});

// テキストファイル書き込み
await writeTextFile('data.json', JSON.stringify(data), {
  baseDir: BaseDirectory.AppData,
});

// ディレクトリ一覧
const entries = await readDir('my-folder', {
  baseDir: BaseDirectory.AppData,
});

// ディレクトリ作成
await mkdir('new-folder', {
  baseDir: BaseDirectory.AppData,
  recursive: true,
});

// ファイル削除
await remove('old-file.txt', { baseDir: BaseDirectory.AppData });

// 存在確認
const fileExists = await exists('config.json', {
  baseDir: BaseDirectory.AppConfig,
});
```

### store（永続化 KVS）

```bash
cargo add tauri-plugin-store
npm install @tauri-apps/plugin-store
```

```typescript
import { load } from '@tauri-apps/plugin-store';

const store = await load('settings.json', { autoSave: false });

// 読み書き
await store.set('theme', 'dark');
const theme = await store.get<string>('theme');

// 削除
await store.delete('old-key');

// 全キー取得
const keys = await store.keys();

// ディスクに保存
await store.save();
```

---

## UI・ダイアログ系

### dialog（ファイルダイアログ）

```bash
cargo add tauri-plugin-dialog
npm install @tauri-apps/plugin-dialog
```

```typescript
import { open, save, message, ask, confirm } from '@tauri-apps/plugin-dialog';

// ファイル選択
const selected = await open({
  multiple: false,
  filters: [{ name: 'Images', extensions: ['png', 'jpg', 'jpeg'] }],
});

// 複数ファイル選択
const files = await open({ multiple: true });

// ディレクトリ選択
const dir = await open({ directory: true });

// 保存ダイアログ
const savePath = await save({
  filters: [{ name: 'JSON', extensions: ['json'] }],
  defaultPath: 'output.json',
});

// メッセージダイアログ
await message('Operation completed!', { title: 'Success', kind: 'info' });

// 確認ダイアログ
const confirmed = await confirm('Are you sure?', { title: 'Confirm' });

// Yes/No ダイアログ
const answer = await ask('Do you want to save?', { title: 'Save', kind: 'warning' });
```

### notification（システム通知）

```bash
cargo add tauri-plugin-notification
npm install @tauri-apps/plugin-notification
```

```typescript
import {
  sendNotification,
  requestPermission,
  isPermissionGranted,
} from '@tauri-apps/plugin-notification';

// 権限確認・要求
let permissionGranted = await isPermissionGranted();
if (!permissionGranted) {
  const permission = await requestPermission();
  permissionGranted = permission === 'granted';
}

// 通知送信
if (permissionGranted) {
  sendNotification({
    title: 'Update Available',
    body: 'A new version is ready to install.',
    icon: 'icons/icon.png',
  });
}
```

---

## ネットワーク系

### http（HTTP クライアント）

```bash
cargo add tauri-plugin-http
npm install @tauri-apps/plugin-http
```

```json
// capabilities/default.json
{
  "permissions": [
    {
      "identifier": "http:default",
      "allow": [{ "url": "https://api.example.com/**" }]
    }
  ]
}
```

```typescript
import { fetch } from '@tauri-apps/plugin-http';

// GET リクエスト
const response = await fetch('https://api.example.com/data');
const data = await response.json();

// POST リクエスト
const result = await fetch('https://api.example.com/items', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ name: 'item', value: 42 }),
});
```

### websocket（WebSocket クライアント）

```bash
cargo add tauri-plugin-websocket
npm install @tauri-apps/plugin-websocket
```

```typescript
import WebSocket from '@tauri-apps/plugin-websocket';

const ws = await WebSocket.connect('ws://localhost:8080');

ws.addListener((msg) => {
  console.log('Received:', msg);
});

await ws.send('Hello, Server!');
await ws.disconnect();
```

---

## システム連携系

### shell（シェル・外部アプリ連携）

```bash
cargo add tauri-plugin-shell
npm install @tauri-apps/plugin-shell
```

```typescript
import { open, Command } from '@tauri-apps/plugin-shell';

// URL をデフォルトブラウザで開く
await open('https://tauri.app');

// ファイルをデフォルトアプリで開く
await open('/path/to/file.pdf');

// シェルコマンド実行（capabilities でスコープ設定が必要）
const command = Command.create('echo', ['Hello, World!']);
const output = await command.execute();
console.log(output.stdout);

// 長時間プロセスの出力をストリーミング
const child = await Command.create('long-process').spawn();
child.stdout.on('data', (data) => console.log(data));
await child.kill();
```

### global-shortcut（グローバルショートカット）

```bash
cargo add tauri-plugin-global-shortcut
npm install @tauri-apps/plugin-global-shortcut
```

```typescript
import { register, unregister } from '@tauri-apps/plugin-global-shortcut';

// グローバルショートカット登録
await register('CmdOrCtrl+Shift+P', () => {
  console.log('Shortcut triggered!');
});

// 解除
await unregister('CmdOrCtrl+Shift+P');
```

### clipboard-manager（クリップボード）

```bash
cargo add tauri-plugin-clipboard-manager
npm install @tauri-apps/plugin-clipboard-manager
```

```typescript
import { readText, writeText } from '@tauri-apps/plugin-clipboard-manager';

// クリップボードから読み取り
const text = await readText();

// クリップボードに書き込み
await writeText('Copied to clipboard!');
```

### os（OS 情報）

```bash
cargo add tauri-plugin-os
npm install @tauri-apps/plugin-os
```

```typescript
import { platform, version, type, arch } from '@tauri-apps/plugin-os';

const os = platform();  // 'linux' | 'windows' | 'macos' | 'android' | 'ios'
const osVersion = version();  // '11.0.0' など
const osType = type();  // 'Linux' | 'Windows_NT' | 'Darwin' など
const architecture = arch();  // 'x86_64' | 'aarch64' など
```

### process（プロセス制御）

```bash
cargo add tauri-plugin-process
npm install @tauri-apps/plugin-process
```

```typescript
import { exit, relaunch } from '@tauri-apps/plugin-process';

// アプリを終了
await exit(0);

// アプリを再起動
await relaunch();
```

---

## データベース系

### sql（SQL データベース）

```bash
cargo add tauri-plugin-sql --features sqlite
npm install @tauri-apps/plugin-sql
```

```typescript
import Database from '@tauri-apps/plugin-sql';

// SQLite 接続
const db = await Database.load('sqlite:my-app.db');

// テーブル作成
await db.execute(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL
  )
`);

// データ挿入
const result = await db.execute(
  'INSERT INTO users (name, email) VALUES ($1, $2)',
  ['Alice', 'alice@example.com']
);
console.log('Inserted ID:', result.lastInsertId);

// データ取得
const users = await db.select<{ id: number; name: string; email: string }[]>(
  'SELECT * FROM users WHERE id > $1',
  [0]
);
```

---

## 認証・セキュリティ系

### stronghold（秘密情報の安全な保存）

```bash
cargo add tauri-plugin-stronghold
npm install @tauri-apps/plugin-stronghold
```

### biometric（生体認証）

```bash
cargo add tauri-plugin-biometric
npm install @tauri-apps/plugin-biometric
```

---

## ウィンドウ・UI 拡張系

### window-state（ウィンドウ状態の永続化）

```bash
cargo add tauri-plugin-window-state
npm install @tauri-apps/plugin-window-state
```

```rust
// 自動的にウィンドウ位置・サイズを記憶
.plugin(tauri_plugin_window_state::Builder::default().build())
```

### autostart（自動起動）

```bash
cargo add tauri-plugin-autostart
npm install @tauri-apps/plugin-autostart
```

```typescript
import { enable, disable, isEnabled } from '@tauri-apps/plugin-autostart';

await enable();
await disable();
const enabled = await isEnabled();
```

### single-instance（多重起動防止）

```bash
cargo add tauri-plugin-single-instance
```

```rust
.plugin(tauri_plugin_single_instance::init(|app, argv, cwd| {
    // 2つ目のインスタンスが起動された時の処理
    app.get_webview_window("main").unwrap().set_focus().unwrap();
}))
```

---

## アップデート系

### updater（自動更新）

```bash
cargo add tauri-plugin-updater
npm install @tauri-apps/plugin-updater
```

```typescript
import { check } from '@tauri-apps/plugin-updater';
import { relaunch } from '@tauri-apps/plugin-process';

const update = await check();
if (update?.available) {
  console.log(`Update available: ${update.version}`);
  await update.downloadAndInstall();
  await relaunch();
}
```

---

## プラグイン一覧（カテゴリ別）

| カテゴリ | プラグイン名 |
|----------|-------------|
| ファイル | `fs`, `store`, `stronghold` |
| UI | `dialog`, `notification`, `window-state` |
| ネットワーク | `http`, `websocket` |
| システム | `shell`, `os`, `process`, `global-shortcut`, `clipboard-manager` |
| データベース | `sql` |
| 認証 | `biometric`, `stronghold` |
| アップデート | `updater` |
| アプリ管理 | `autostart`, `single-instance`, `deep-link` |
| モバイル | `geolocation`, `barcode-scanner`, `haptics`, `nfc` |
| ログ | `log` |

公式ドキュメント: https://v2.tauri.app/plugin/
