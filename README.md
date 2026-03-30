# C2Lab

Claude Code（C2）の実験場（Lab）です。
Hook, Slash Command, SubAgent, Skill をプロジェクトごとに用意するのは面倒なので、再利用可能なプラグインリポジトリとしてまとめています。

## プラグイン導入方法

### Step 1: マーケットプレイスを追加する

Claude Code 内で以下のコマンドを実行します:

```
/plugin marketplace add UtakataKyosui/C2Lab
```

または、`.claude/settings.json` に直接記述することもできます:

```json
{
  "extraKnownMarketplaces": {
    "utakata-plugins": {
      "source": {
        "source": "github",
        "repo": "UtakataKyosui/C2Lab"
      }
    }
  }
}
```

### Step 2: プラグインをインストールする

マーケットプレイス追加後、`/plugin` で UI を開いて使いたいプラグインを選択するか、CLI でインストールします:

```bash
# 例: jj-vcs-workflow をインストール
claude plugin install jj-vcs-workflow@utakata-plugins

# プロジェクトスコープ（チーム共有）でインストール
claude plugin install jj-vcs-workflow@utakata-plugins --scope project
```

### スコープについて

| スコープ | 保存先 | 用途 |
|---|---|---|
| `user`（デフォルト） | `~/.claude/settings.json` | 個人の全プロジェクトで使用 |
| `project` | `.claude/settings.json` | チームで共有 |
| `local` | `.claude/settings.local.json` | 個人用・gitignore 済み |

## プラグイン一覧

### VCS / ワークフロー

| プラグイン | 説明 |
|---|---|
| **jj-vcs-workflow** | Jujutsu (jj) の総合ガイド。基本コマンド・Git 移行・並列開発・履歴操作・安全な push ワークフロー |
| **review-workflow** | PR レビュー対応の自動化。コメント取得→修正→検証→コミット→Push を Python で制御 |
| **pr-lifecycle** | PR ライフサイクル管理。CI ローカル検証・PR 作成・マージ準備を標準化 |
| **gh** | GitHub CLI (gh) のパーミッションルールと使用ガイド |
| **vibe-kanban** | vibe-kanban によるローカル AI エージェントのタスク管理最適化 |

### 開発ツール

| プラグイン | 説明 |
|---|---|
| **rust** | Rust 開発支援。コードレビュー・デバッグ・最適化エージェントとフック |
| **code-review** | 汎用コードレビュー。レビュー原則とチェックリストコマンド |
| **tdd-enforce** | TDD を強制。テストなしの実装をブロックする多言語対応フック |
| **wasm-optimizer** | JS/TS の重い処理を検出し、WebAssembly ライブラリへの置き換えを提案 |
| **scaffdog-colocation** | scaffdog を使ったコロケーションパターンによるファイル分割支援 |
| **playwright-e2e-tester** | Playwright による Web アプリ E2E テスト自動化。開発確認・PR レビュー確認の 2 エージェント |
| **color-distance** | WCAG コントラスト比・Delta E・RGB 距離による色アクセシビリティ測定 |

### Tauri / デスクトップ

| プラグイン | 説明 |
|---|---|
| **tauri-app-dev** | Tauri v2 アプリ開発ガイド。IPC・capabilities・モバイル対応・公式プラグイン活用 |
| **tauri-plugin-dev** | Tauri v2 プラグイン開発ガイド。スキャフォールド・Rust/TypeScript パターン・テスト |
| **obs-plugin-dev** | OBS Studio プラグイン開発支援。C/C++・Rust FFI・CMake・テスト |

### パッケージマネージャ / ツールチェーン

| プラグイン | 説明 |
|---|---|
| **npm** | npm / npx のパーミッションルールと使用ガイド |
| **pnpm** | pnpm / pnpx のパーミッションルールと使用ガイド |
| **yarn** | Yarn のパーミッションルールと使用ガイド |
| **bun** | Bun ランタイム・パッケージマネージャのパーミッションルールと使用ガイド |
| **uv** | Python uv / uvx のパーミッションルールと使用ガイド |
| **mise** | mise（多言語バージョンマネージャ）のパーミッションルールと使用ガイド |
| **moonrepo** | Moonrepo (Task Runner) + proto (Toolchain Manager) のガイド |

### AI / 知識管理

| プラグイン | 説明 |
|---|---|
| **obsidian-bridge** | Obsidian Vault を長期記憶基盤として活用。Claude メモリ自動同期・Vault 想起・知識キャプチャを統合 |
| **ollama-consult** | ローカル LLM (Ollama) を Claude の計画・方針の壁打ち相手として活用 |

### オブザーバビリティ

| プラグイン | 説明 |
|---|---|
| **otel-telemetry** | OpenTelemetry テレメトリを自動設定。OTLP 経由で OpenObserve にメトリクス・ログを送信 |

### 技術リファレンス

| プラグイン | 説明 |
|---|---|
| **protobuf** | Protocol Buffers のスタイルガイド・ツール使用例 |
| **activitypub** | ActivityPub C2S インタラクションの実装支援 |
| **poml-assist** | Microsoft POML によるプロンプト設計支援。バリデーション・レンダリング付き |

### コンテンツ

| プラグイン | 説明 |
|---|---|
| **zenn-review** | Zenn 記事・書籍のレビュー。誤字脱字・構文・フロントマター・章間整合性チェック |

## ディレクトリ構成

```
C2Lab/
├── .claude-plugin/          # マーケットプレイスメタデータ (marketplace.json)
├── plugins/                 # 各種プラグイン
│   ├── activitypub/
│   ├── bun/
│   ├── code-review/
│   ├── color-distance/
│   ├── gh/
│   ├── jj-vcs-workflow/
│   ├── mise/
│   ├── moonrepo/
│   ├── npm/
│   ├── obs-plugin-dev/
│   ├── obsidian-bridge/
│   ├── ollama-consult/
│   ├── otel-telemetry/
│   ├── playwright-e2e-tester/
│   ├── pnpm/
│   ├── poml-assist/
│   ├── pr-lifecycle/
│   ├── protobuf/
│   ├── review-workflow/
│   ├── rust/
│   ├── scaffdog-colocation/
│   ├── tauri-app-dev/
│   ├── tauri-plugin-dev/
│   ├── tdd-enforce/
│   ├── uv/
│   ├── vibe-kanban/
│   ├── wasm-optimizer/
│   ├── yarn/
│   └── zenn-review/
├── jj-config/               # Jujutsu (jj) 設定ファイル
└── scripts/                 # リント・チェック用スクリプト
```

各プラグインは以下のコンポーネントを任意に含みます:

- `skills/` — コンテキストとして読み込まれるナレッジベース
- `commands/` — `/command-name` で呼び出せるスラッシュコマンド
- `agents/` — 特定タスクに特化したサブエージェント
- `hooks/` — ツール実行前後に自動実行されるフック
