---
name: obsidian-memory
description: Claude Code のメモリを Obsidian Vault に同期し、グラフ上の関係性を探索するスキル。記憶の書き込み・読み出し・想起（関連ノート検索）を Obsidian CLI 経由で実行する。
---

# obsidian-memory スキル

Claude Code のメモリファイル (`~/.claude/projects/*/memory/*.md`) を Obsidian Vault と双方向に連携する。

## 前提条件

- Obsidian 1.12+ がインストールされていること
- CLI 有効化: Settings → General → Command line interface
- 環境変数の設定（どちらか一方）:
  - `OBSIDIAN_VAULT_NAME="My Vault"` （推奨。CLI がパスを自動解決）
  - `OBSIDIAN_VAULT_PATH="/path/to/vault"` （フォールバック）

## 操作一覧

### 1. メモリを Obsidian へ同期する

全メモリファイルを Vault の `Claude-Memory/` ディレクトリに同期する:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/hooks/scripts/sync-memory.py" --all
```

frontmatter の `type` フィールドでサブフォルダに自動分類される:
```
Vault/Claude-Memory/
├── MEMORY.md          # インデックス
├── user/              # type: user
├── feedback/          # type: feedback
├── project/           # type: project
└── reference/         # type: reference
```

### 2. グラフ上の関係性を探索する

#### 特定ノートへのバックリンクを調べる

```bash
obsidian vault="$OBSIDIAN_VAULT_NAME" backlinks file="<note-name>"
```

例: あるメモリノートが他のノートからどう参照されているかを確認:
```bash
obsidian vault="$OBSIDIAN_VAULT_NAME" backlinks file="user_role"
```

#### ノートの発リンクを調べる

```bash
obsidian vault="$OBSIDIAN_VAULT_NAME" links file="<note-name>"
```

#### 関連ノートを全文検索する

```bash
obsidian vault="$OBSIDIAN_VAULT_NAME" search query="<キーワード>"
```

文脈付きで検索（行内容も返す）:
```bash
obsidian vault="$OBSIDIAN_VAULT_NAME" search:context query="<キーワード>"
```

#### タグで関連ノートを探す

```bash
obsidian vault="$OBSIDIAN_VAULT_NAME" tags counts
obsidian vault="$OBSIDIAN_VAULT_NAME" tag name="<tag>" verbose
```

### 3. Obsidian からノートを読み込む（想起）

```bash
obsidian vault="$OBSIDIAN_VAULT_NAME" read file="<note-name>"
```

例: プロジェクト記憶を取得:
```bash
obsidian vault="$OBSIDIAN_VAULT_NAME" read path="Claude-Memory/project/<filename>.md"
```

### 4. Vault 内のメモリノート一覧を取得する

```bash
obsidian vault="$OBSIDIAN_VAULT_NAME" files folder="Claude-Memory"
```

## 符号化特異性を使った想起（Encoding Specificity）

「記憶が符号化されたコンテキストと同じコンテキストで検索すると想起精度が上がる」原理を活用する。

同期時に各メモリノートへ以下のプロパティが自動注入される:

```yaml
context_project:   C2Lab          # 記録時のプロジェクト名
context_synced_at: 2026-03-12T...  # 同期タイムスタンプ
context_tags:
  - C2Lab
```

### プロジェクト絞り込み検索

Obsidian の検索構文でプロパティフィルタを使用:

```bash
# 特定プロジェクトのメモリのみ検索
obsidian vault="$OBSIDIAN_VAULT_NAME" search query='[context_project:C2Lab] <keyword>'

# プロジェクト横断で検索（全メモリ対象）
obsidian vault="$OBSIDIAN_VAULT_NAME" search:context query="<keyword>"
```

### どのプロジェクトの記憶が存在するか確認

```bash
obsidian vault="$OBSIDIAN_VAULT_NAME" properties name=context_project counts
```

### コンテキスト付き想起の手順

現在作業中のプロジェクトに関連する記憶を想起する場合:

1. 現在のプロジェクト名を特定（例: `C2Lab`）
2. プロジェクト絞り込み + キーワードで検索:
   ```bash
   obsidian vault="$OBSIDIAN_VAULT_NAME" search:context query='[context_project:C2Lab] <topic>'
   ```
3. ヒットしたノートのバックリンクを確認: `backlinks file="<hit>"`
4. 別プロジェクトへの関連があれば横断検索で補完

## 想起フロー（Spreading Activation + Encoding Specificity）

関連記憶を連鎖的に探索する際の手順:

1. **コンテキスト絞り込み検索**: `search:context query='[context_project:<project>] <topic>'`
2. **近傍ノードへの拡散**: ヒットしたノートの `backlinks` を確認
3. **タグクラスター横断**: `tag name="<tag>" verbose`
4. **必要なノートを読み込み**: `read file="<note>"`
5. **コンテキスト外への拡張**: プロジェクト絞りを外して全体検索で補完

## エージェントへの指示

このスキルを使うべきシーン:
- ユーザーが「Obsidian に同期して」と依頼したとき
- 会話の文脈で過去の記憶の参照が必要なとき（`search` で探索）
- 記憶の関連性をグラフで確認したいとき（`backlinks` / `links`）
- セッション開始時に過去のプロジェクト記憶を想起したいとき
