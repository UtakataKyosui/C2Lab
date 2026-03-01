# tauri-dev

Tauri v2プラグイン開発を支援するClaude Codeプラグイン。

公式・コミュニティに存在しないカスタムTauriプラグインの新規作成、エコシステム調査、実装パターンの提供を行います。

## 機能

- **Skill**: Tauri v2プラグイン開発の知識（構造・Rustパターン・TypeScriptバインディング・テスト）
- **Agent - tauri-plugin-creator**: 新規プラグインのスキャフォールドと初期実装生成
- **Agent - tauri-plugin-researcher**: 既存プラグインの調査と実装アプローチの提案
- **Hook**: `lib.rs`編集時のTauriプラグイン必須パターン検証

## 使い方

### 新規プラグインを作成する

```
Tauriのファイル監視プラグインを作りたい
```

`tauri-plugin-creator` エージェントが起動し、要件を確認してスキャフォールドします。

### 既存プラグインを調べる

```
Tauriでクリップボードを操作するプラグインはある？
```

`tauri-plugin-researcher` エージェントが公式・コミュニティプラグインを調査します。

### 実装方法を学ぶ

```
Tauri v2のプラグインでコマンドを定義するには？
```

Skill が Tauri v2 プラグインのパターンと実装方法を提供します。

## 前提条件

- Rust / Cargo がインストールされていること
- Tauri CLI v2 (`cargo install tauri-cli` または `npm install -g @tauri-apps/cli`)
- Node.js / pnpm (TypeScriptバインディングを生成する場合)

## ディレクトリ構造

```
plugins/tauri-plugin-dev/
├── .claude-plugin/
│   └── plugin.json
├── skills/
│   └── tauri-plugin-dev/
│       ├── SKILL.md
│       └── references/
│           ├── plugin-structure.md
│           ├── rust-patterns.md
│           ├── typescript-bindings.md
│           ├── testing-debugging.md
│           └── mobile-support.md
├── agents/
│   ├── tauri-plugin-creator.md
│   └── tauri-plugin-researcher.md
├── hooks/
│   └── hooks.json
└── README.md
```
