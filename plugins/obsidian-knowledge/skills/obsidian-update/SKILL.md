---
name: obsidian-update
description: >
  過去のノートの内容が間違っていた・古くなったと判明した際に、
  該当ノートを検索・読み込み・修正・保存する（再固定化）。
  「Obsidianのノートを修正して」「あのメモが間違ってた」「Vaultを更新して」
  「古い情報を直して」といった指示で使用する。
---

# obsidian-update

過去ノートの誤りや陳腐化した情報を修正する（再固定化）。

## 再固定化とは

人間の記憶は想起されるたびに一時的に不安定になり、最新情報で書き換えられる。
この `obsidian-update` は同じプロセスを模倣する：ノートを読み込み、誤りを修正し、更新日時と理由を記録する。

## 手順

1. **修正対象のノートを検索する**

   ```bash
   obsidian vault="$OBSIDIAN_VAULT_NAME" search query="<修正対象のキーワード>"
   ```

2. **現在の内容を確認する**

   ```bash
   obsidian vault="$OBSIDIAN_VAULT_NAME" read file="<ノート名>"
   ```

3. **新情報で内容を書き換える**

   ```bash
   obsidian vault="$OBSIDIAN_VAULT_NAME" create name="<ノート名>" overwrite content="<新しい内容>"
   ```

4. **ノート末尾に更新日時と修正理由を記録する**

   書き換え後のコンテンツに以下を含める:
   ```markdown
   ---
   > YYYY-MM-DD 更新：<修正理由>
   > 例: 2026-03-13 更新：v2.0 で API 仕様が変わったため修正
   ```

## パスを指定して上書きする場合

ノート名が一意でない場合はパス指定:
```bash
obsidian vault="$OBSIDIAN_VAULT_NAME" create \
  name="<ノート名>" \
  path="knowledge/" \
  overwrite \
  content="<新しい内容>"
```

## 使用例

```bash
# 古い jj コマンドのメモを検索
obsidian vault="$OBSIDIAN_VAULT_NAME" search query="jj rebase deprecated"

# 内容を確認
obsidian vault="$OBSIDIAN_VAULT_NAME" read file="jj-rebase-guide"

# 修正後の内容で上書き（更新履歴を末尾に追加）
obsidian vault="$OBSIDIAN_VAULT_NAME" create \
  name="jj-rebase-guide" \
  path="knowledge/" \
  overwrite \
  content="# jj rebase ガイド\n\n...(修正内容)...\n\n---\n> 2026-03-13 更新：jj 0.25 で --skip-emptied フラグが追加されたため修正"
```
