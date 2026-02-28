# tauri-app-dev

Tauri v2 **アプリケーション**開発を支援するプラグイン。

> **既存の `tauri-dev` との違い**
> - `tauri-dev` → Tauri **プラグイン**を作る人向け（Rust プラグイン SDK, TypeScript バインディング生成）
> - `tauri-app-dev` → Tauri で**アプリ**を作る人向け（プロジェクト構造, IPC, セキュリティ, モバイル対応）

## 提供する機能

| コンポーネント | 内容 |
|--------------|------|
| **Skill** | `tauri-app-dev` - Tauri v2 アプリ開発の包括的知識ベース |
| **Agent** | `tauri-app-scaffold` - 新規プロジェクト作成・アーキテクチャ設計 |
| **Agent** | `tauri-capability-config` - capabilities / CSP 設定支援 |
| **Hook** | `PreToolUse` - capabilities JSON・tauri.conf.json の構造検証 |

## スキルのトリガー例

- "Tauri でアプリを作りたい"
- "Tauri プロジェクトを始める"
- "Tauri の IPC 通信を実装"
- "tauri.conf.json を設定したい"
- "capabilities を設定したい"
- "Tauri モバイルアプリ開発"
- "Tauri v2 のセキュリティ設定"
- "公式プラグインの使い方"

## エージェントの使い方

### tauri-app-scaffold

新規プロジェクトのセットアップやアーキテクチャ設計に使用:

- "新しい Tauri アプリを作りたい"
- "既存の React プロジェクトに Tauri を追加したい"
- "Tauri プロジェクトの構成を決めたい"

### tauri-capability-config

capabilities や CSP の問題解決に使用:

- "capabilities を設定したい"
- "Not allowed by scope エラーが出る"
- "CSP エラーが出る"
- "モバイルでのみ位置情報を使いたい"

## スキルの参考資料

`skills/tauri-app-dev/references/` に詳細な知識ベースがある:

| ファイル | 内容 |
|---------|------|
| `project-structure.md` | プロジェクト構成・tauri.conf.json 全設定項目 |
| `ipc-patterns.md` | invoke/events/channels の実装例（Rust + TypeScript） |
| `security-capabilities.md` | capabilities JSON・CSP 設定・権限一覧 |
| `mobile-development.md` | iOS/Android 開発・TAURI_DEV_HOST 設定 |
| `frontend-integration.md` | React/Vue/Svelte/Next.js 統合 |
| `official-plugins.md` | 公式プラグイン 40+ 一覧・インストール方法 |
| `build-deploy.md` | ビルド・コード署名・クロスコンパイル・GitHub Actions |

## フック（自動バリデーション）

`capabilities/*.json` または `tauri.conf.json` を書き込む際に自動的に構造を検証する:

- `capabilities` JSON の `identifier` フィールドの存在確認
- `permissions` / `windows` / `platforms` フィールドの型チェック
- `tauri.conf.json` の基本構造確認（`productName`, `identifier`, ウィンドウの `label`）

## バージョン

`0.1.0` - Tauri v2 対応
