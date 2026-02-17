# JJ リビジョン指定方法

jjでは柔軟なリビジョン指定（revset）が可能です。コマンドの`-r`オプションなどで使用します。

## 基本的なリビジョン指定

| 指定方法 | 説明 | 例 |
|---------|------|-----|
| `@` | 現在のワーキングコピー | `jj diff -r @` |
| `@-` | 現在の親（1つ前） | `jj show @-` |
| `@--` | 親の親（2つ前） | `jj diff -r @--` |
| `@---` | 3つ前 | 以降同様 |

## ID による指定

| 指定方法 | 説明 | 例 |
|---------|------|-----|
| `<change_id>` | チェンジID | `jj show abc123` |
| `<commit_id>` | コミットID | `jj show def456` |
| 短縮形 | IDの先頭数文字 | `jj show abc` |

**補足**: jjでは「チェンジID」と「コミットID」は異なります。
- チェンジID: チェンジを一意に識別（修正しても変わらない）
- コミットID: コミットのハッシュ（修正すると変わる）

## ブックマーク・タグによる指定

| 指定方法 | 説明 | 例 |
|---------|------|-----|
| `<bookmark>` | ブックマーク名 | `jj log -r main` |
| `<bookmark>@<remote>` | リモートブックマーク | `jj log -r main@origin` |
| `<tag>` | タグ名 | `jj show v1.0.0` |

## 特殊なリビジョン

| 指定方法 | 説明 |
|---------|------|
| `root()` | ルートコミット（最初の空コミット） |
| `heads()` | すべてのヘッド |
| `visible_heads()` | 可視ヘッド |
| `trunk()` | トランク（mainなどのメインライン） |

## 親子関係の演算子

| 演算子 | 説明 | 例 |
|-------|------|-----|
| `-` | 親（複数可） | `main-`, `main--` |
| `+` | 子（複数可） | `root()+` |
| `::` | 祖先すべて | `::main` |
| `..` | 範囲 | `main..@` |

## Revset 式（高度な指定）

### 祖先・子孫

```bash
# mainの祖先すべて
jj log -r "::main"

# @の子孫すべて
jj log -r "@::"

# mainから@までの範囲
jj log -r "main..@"

# main以降のコミット（main含まない）
jj log -r "main.."
```

### 集合演算

```bash
# 和集合（AまたはB）
jj log -r "main | feature"

# 積集合（AかつB）
jj log -r "main & feature"

# 差集合（AからBを除く）
jj log -r "main ~ feature"
```

### フィルター関数

```bash
# 空でないチェンジ
jj log -r "~empty()"

# 説明に"fix"を含む
jj log -r 'description("fix")'

# 特定の作者
jj log -r 'author("name@example.com")'

# 特定ファイルを変更したチェンジ
jj log -r 'file("src/main.rs")'

# マージコミット
jj log -r "merges()"

# コンフリクトがあるチェンジ
jj log -r "conflict()"
```

### 便利な組み合わせ

```bash
# mainにない自分の変更
jj log -r "mine() ~ ::main"

# 最近の10件
jj log -r "@:: | @-:: | @--::" --limit 10

# すべてのブックマーク
jj log -r "bookmarks()"

# リモートブックマーク
jj log -r "remote_bookmarks()"

# 未プッシュの変更
jj log -r "mine() ~ ::main@origin"
```

## 実践的な使用例

### 特定の範囲をリベース

```bash
# feature-xブランチをmainの先頭にリベース
jj rebase -b feature-x -d main
```

### 特定のチェンジの差分を確認

```bash
# 3つ前のチェンジの差分
jj diff -r @---

# mainとの差分
jj diff --from main --to @
```

### 履歴の検索

```bash
# "bug"を含む説明のチェンジを検索
jj log -r 'description("bug")'

# 特定ファイルの変更履歴
jj log -r 'file("README.md")'
```

### ブックマーク操作

```bash
# 現在のチェンジにブックマーク作成
jj bookmark create feature-y -r @

# mainブックマークを現在位置に移動
jj bookmark move main --to @
```

## Tips

1. **短縮形を活用**: IDは一意に特定できる最短の文字数でOK
2. **@を基準に**: `@-`、`@--`で相対的に指定できる
3. **revset式はクォート**: シェルで特殊文字として解釈されないよう`""`で囲む
4. **`jj log -r`で確認**: 複雑なrevset式は先に`jj log`で確認すると安全
