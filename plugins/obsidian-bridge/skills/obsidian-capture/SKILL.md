---
name: obsidian-capture
description: >
  セッション中に得た知見・エラーの原因・ライブラリの使い方などを
  Obsidian Vault の適切なノートへ書き込む。
  「Obsidianに記録して」「Vaultに書いておいて」「この知識を保存して」
  といった指示、またはエラー解決・技術調査が完了した直後に使用する。
  エピソード記憶は daily/、意味記憶は knowledge/、ルールは procedures/ へ振り分ける。
---

# obsidian-capture

セッション中に得た知見を Obsidian Vault へ書き込む。

## 前提

環境変数 `OBSIDIAN_VAULT_NAME`（推奨）または `OBSIDIAN_VAULT_PATH` が設定されていること。

## Vault ディレクトリと記憶タイプの対応

| ディレクトリ | 記憶タイプ | 書き込む内容 |
| --- | --- | --- |
| `daily/YYYY-MM-DD.md` | エピソード記憶 | その日限りの出来事・意思決定・作業ログ |
| `knowledge/<トピック>.md` | 意味記憶 | 再利用可能な技術知識・ライブラリの挙動・デバッグのコツ |
| `procedures/<ルール名>.md` | 手続き記憶 | プロジェクト横断のルール・CLAUDE.md を補完する手順 |
| `shared/<テーマ>.md` | 共通ナレッジ | リポジトリを跨いで使い回す汎用知識 |

## 手順

1. **カテゴリを判断する**
   - 「今日このプロジェクトでこうした」→ `daily/`
   - 「このライブラリはこう使う」「このエラーはこれが原因」→ `knowledge/`
   - 「このプロジェクトではこのルールに従う」→ `procedures/`
   - 複数リポジトリで使える知識 → `shared/`

2. **既存ノートへ追記する場合**

   ```bash
   obsidian vault="$OBSIDIAN_VAULT_NAME" append file="knowledge/<トピック>" content="<追記内容>"
   ```

   デイリーノートへ追記:
   ```bash
   obsidian vault="$OBSIDIAN_VAULT_NAME" daily:append content="<追記内容>"
   ```

3. **新規ノートを作成する場合**

   ```bash
   obsidian vault="$OBSIDIAN_VAULT_NAME" create name="<ノート名>" path="knowledge/" content="<内容>"
   ```

4. **知識グラフを繋げる**

   書き込んだ内容に関連ノートへの `[[リンク]]` を付与する。
   例: `knowledge/react-hooks.md` に書くなら `[[React]]` `[[useState]]` を含める。

## 書き込み例

```bash
# ライブラリの挙動を knowledge/ に保存
obsidian vault="$OBSIDIAN_VAULT_NAME" create \
  name="jj-conflict-resolution" \
  path="knowledge/" \
  content="# jj コンフリクト解消\n\n## 手順\n...\n\n## 関連\n[[jj]] [[VCS]]"

# 今日の意思決定を daily/ に記録
obsidian vault="$OBSIDIAN_VAULT_NAME" daily:append \
  content="## C2Lab\n- obsidian-knowledge プラグイン設計を決定 [[obsidian-knowledge]]"
```
