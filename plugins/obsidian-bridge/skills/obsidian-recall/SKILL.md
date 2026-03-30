---
name: obsidian-recall
description: >
  タスクのキーワードで Obsidian Vault を検索し、関連するノートの内容をコンテキストに展開する。
  「Obsidian を検索して」「過去の知識を調べて」「Vault に何かある？」
  「このエラー前に見たことある？」といった指示、または作業開始時に使用する。
---

# obsidian-recall

タスク開始前に Vault を検索し、関連する過去の知見をコンテキストへ読み込む。

## 前提

環境変数 `OBSIDIAN_VAULT_NAME`（推奨）または `OBSIDIAN_VAULT_PATH` が設定されていること。

## 手順

1. **キーワードで全文検索する**

   ```bash
   obsidian vault="$OBSIDIAN_VAULT_NAME" search query="<キーワード>"
   ```

   文脈付きで検索（行内容も確認したい場合）:
   ```bash
   obsidian vault="$OBSIDIAN_VAULT_NAME" search:context query="<キーワード>"
   ```

2. **ヒットしたノートを読み込む**

   ```bash
   obsidian vault="$OBSIDIAN_VAULT_NAME" read file="<ノート名>"
   ```

3. **バックリンクでリンクしている隣接ノートも参照する**

   ```bash
   obsidian vault="$OBSIDIAN_VAULT_NAME" backlinks file="<ノート名>"
   ```

4. **読み込んだ内容を踏まえて作業を開始する**

## 探索の深め方

関連記憶を連鎖的に探索する場合:

1. キーワード検索でエントリーポイントを見つける
2. ヒットしたノートの `backlinks` で参照元を確認
3. タグクラスターを横断: `tag name="<tag>" verbose`
4. 必要なノートを `read` で読み込む

### タグ検索

```bash
# タグ一覧と件数
obsidian vault="$OBSIDIAN_VAULT_NAME" tags counts

# 特定タグのノート一覧
obsidian vault="$OBSIDIAN_VAULT_NAME" tag name="<tag>" verbose
```

### フォルダ別に絞り込む

```bash
# knowledge/ 内のノート一覧
obsidian vault="$OBSIDIAN_VAULT_NAME" files folder="knowledge"

# procedures/ 内のルール確認
obsidian vault="$OBSIDIAN_VAULT_NAME" files folder="procedures"
```

## 使用例

```bash
# React hooks に関する過去の知見を検索
obsidian vault="$OBSIDIAN_VAULT_NAME" search:context query="React hooks"

# 見つかったノートを読み込む
obsidian vault="$OBSIDIAN_VAULT_NAME" read file="react-hooks"

# そのノートを参照しているノートも確認
obsidian vault="$OBSIDIAN_VAULT_NAME" backlinks file="react-hooks"
```
