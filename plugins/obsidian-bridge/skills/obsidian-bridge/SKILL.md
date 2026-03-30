---
name: obsidian-bridge
description: >
  Obsidian Vault を Claude Code の長期記憶基盤として活用するプラグインの概要。
  Claude メモリ同期・Vault 想起・知識キャプチャの3機能を提供する。
  「Obsidian の機能を確認したい」「どのスキルを使えばいい？」といった場合に使用。
---

# obsidian-bridge

Claude Code の長期記憶を Obsidian Vault と統合するプラグイン。

## 機能概要

| 機能 | スキル | 動作 |
| --- | --- | --- |
| Claude メモリ → Vault 自動同期 | — | 自動（Write / SessionEnd フック） |
| 自動 Vault 検索によるリコール | — | 自動（UserPromptSubmit フック、`vault-recall.py`） |
| 知識の記録 | obsidian-capture | 手動 |
| セッション振り返り | obsidian-consolidate | 手動 |
| ノートの修正・更新 | obsidian-update | 手動 |

※ 自動リコールは UserPromptSubmit フック用スクリプト（`vault-recall.py`）が実行します。`obsidian-recall` スキルは、Vault を手動で検索したい場合に使用します。

## 前提条件

- Obsidian 1.12+ がインストールされていること
- CLI 有効化: Settings → General → Command line interface
- 環境変数の設定（どちらか一方）:
  - `OBSIDIAN_VAULT_NAME="My Vault"` （推奨。CLI がパスを自動解決）
  - `OBSIDIAN_VAULT_PATH="/path/to/vault"` （フォールバック）

## 自動フック

### UserPromptSubmit: リコール

毎プロンプトに Vault 検索を実行し、関連ノートをコンテキストに注入する。

**検索戦略（符号化特異性）:**
1. 現在プロジェクトで絞り込み検索: `[context_project:<project>] <keywords>`
2. ヒットなし → プロジェクトフィルタなしの全 Vault 検索
3. Obsidian 未起動 → ローカルメモリファイルを直接検索（フォールバック）

### PostToolUse (Write): メモリ同期

`~/.claude/projects/*/memory/*.md` が Write されるたびに Vault の `Claude-Memory/` へ同期。
符号化コンテキスト（`context_project`, `context_synced_at`）を frontmatter に自動注入する。

### SessionEnd: 全メモリ同期

セッション終了時に全メモリファイルを Vault へ同期する。

## Vault ディレクトリ構造

```
Vault/
├── Claude-Memory/          # Claude Code メモリ同期先
│   ├── MEMORY.md           # インデックス
│   ├── user/               # type: user
│   ├── feedback/           # type: feedback
│   ├── project/            # type: project
│   └── reference/          # type: reference
├── daily/                  # エピソード記憶（作業ログ・意思決定）
├── knowledge/              # 意味記憶（技術知識・ライブラリ挙動）
├── procedures/             # 手続き記憶（プロジェクト横断ルール）
└── shared/                 # 共通ナレッジ（汎用知識）
```

## 使い分けガイド

- **知識をキャプチャしたい** → `obsidian-capture` スキルを使う
- **過去の知識を手動検索したい** → `obsidian-recall` スキルを使う
- **セッションの学びを固定化したい** → `obsidian-consolidate` スキルを使う
- **過去ノートを修正したい** → `obsidian-update` スキルを使う
- **メモリを手動で Vault に同期したい** → `sync-memory.py --all` を実行
