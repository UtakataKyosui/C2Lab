---
name: コンテキスト生成（repomix + rtk）
description: This skill should be used when the user wants to "コードベースを圧縮", "コンテキストを生成", use "repomix", reduce tokens with "rtk", "次セッションにコンテキストを渡す", "AI にコードベース全体を把握させる", or when automating repomix in a Stop hook. Also activates when the user asks about "CONTEXT.md の生成", "コードベースを 1 ファイルにまとめる", or "トークン削減".
version: 0.1.0
---

# コンテキスト生成（repomix + rtk）

`repomix` はコードベースを 1 ファイルに圧縮し、AI が一度に把握できる形式に変換するツール。`rtk` はコマンド出力をパイプで受け取り、AI に渡るトークン量を削減する。両ツールを組み合わせて効率的なコンテキスト管理を実現する。

## repomix — コードベースの圧縮

### 基本使用法

```bash
# カレントディレクトリを圧縮して出力
repomix

# 出力ファイルを指定
repomix --output CONTEXT.md

# 特定ディレクトリを対象に
repomix --include "src/**" --output CONTEXT.md

# 複数のディレクトリを含める
repomix --include "src/**,tests/**" --output CONTEXT.md

# 特定ファイルを除外
repomix --ignore "**/*.test.ts,node_modules/**" --output CONTEXT.md

# XML 形式で出力（AI 解析向け）
repomix --style xml --output CONTEXT.xml

# Markdown 形式で出力（可読性重視）
repomix --style markdown --output CONTEXT.md
```

### 差分ベースの生成（推奨）

Stop Hook では変更ファイルのみを対象にして高速化する:

```bash
# jj で変更ファイルを取得して repomix
jj diff --name-only | tr '\n' ',' | xargs -I {} repomix --include "{}" --output CONTEXT.md

# git で変更ファイルを取得して repomix
git diff --name-only HEAD | tr '\n' ',' | xargs -I {} repomix --include "{}" --output CONTEXT.md

# 変更ファイルが空の場合はスキップ
CHANGED=$(jj diff --name-only 2>/dev/null || git diff --name-only HEAD 2>/dev/null)
if [ -n "$CHANGED" ]; then
  FILES=$(echo "$CHANGED" | tr '\n' ',')
  repomix --include "$FILES" --output CONTEXT.md
fi
```

> **注意**: `git diff` フォールバックは `Bash(git:*)` が許可されている環境でのみ利用可能です。
> jj 専用リポジトリや git コマンドが禁止されている環境では `jj diff --name-only` のみを使用してください。

### 設定ファイルによる制御

プロジェクトルートに `repomix.config.json` を配置すると設定を永続化できる:

```json
{
  "output": {
    "filePath": "CONTEXT.md",
    "style": "markdown",
    "showLineNumbers": false,
    "copyToClipboard": false
  },
  "include": ["src/**", "tests/**"],
  "ignore": {
    "useGitignore": true,
    "useDefaultPatterns": true,
    "customPatterns": ["*.lock", "dist/**", "coverage/**"]
  }
}
```

設定ファイルがある場合はコマンドラインオプションを省略できる:

```bash
repomix  # repomix.config.json を自動読み込み
```

### PreCompact フルスナップショット

コンテキスト圧縮（PreCompact）の直前にコードベース全体のスナップショットを保存する:

```bash
# フルスナップショット
repomix --output CONTEXT_FULL.md

# タイムスタンプ付き
repomix --output "CONTEXT_$(date +%Y%m%d_%H%M%S).md"
```

## rtk — トークン削減パイプ

### 基本使用法

`rtk` は stdout をパイプで受け取り、意味を保ったまま冗長な情報を削除してトークン量を削減する:

```bash
# コマンド出力をトークン削減
<command> | rtk

# rg の出力を削減
rg 'pattern' | rtk

# fd の出力を削減
fd -e ts | rtk

# repomix の出力をさらに削減
repomix --output /dev/stdout | rtk > CONTEXT.md
```

### Hook スクリプトでの活用

Hook スクリプト内で各ツールの出力に `| rtk` を挟む:

```bash
#!/bin/bash
# PostToolUse hook: Semgrep 実行後にトークン削減
FILE="$1"
if command -v semgrep &>/dev/null && command -v rtk &>/dev/null; then
  semgrep --config auto "$FILE" 2>&1 | rtk
elif command -v semgrep &>/dev/null; then
  semgrep --config auto "$FILE" 2>&1
fi
```

### rtk が利用できない場合

rtk が未インストールの場合はパイプを外してそのまま使う:

```bash
# rtk の存在確認
if command -v rtk &>/dev/null; then
  <command> | rtk
else
  <command>
fi
```

## 次セッションへのコンテキスト渡し

### Stop Hook での自動生成フロー

1. セッション終了（Stop イベント）を検知
2. jj/git で変更ファイルを取得
3. repomix で変更ファイルを圧縮 → `CONTEXT.md` に出力
4. 次セッション開始時に `CONTEXT.md` を参照

```bash
# Stop Hook スクリプトの基本フロー
#!/bin/bash
CHANGED=$(jj diff --name-only 2>/dev/null || git diff --name-only HEAD 2>/dev/null)
if [ -z "$CHANGED" ]; then
  exit 0
fi
FILES=$(echo "$CHANGED" | tr '\n' ',')
repomix --include "$FILES" --output CONTEXT.md --style markdown
echo "Context generated: CONTEXT.md"
```

### 次セッション開始時の参照方法

新しいセッションで `CONTEXT.md` を最初に参照する:

```
CONTEXT.md を読んで、前のセッションの作業内容を把握してから作業を再開してください。
```

## repomix の出力形式比較

| 形式 | 用途 | トークン量 |
|---|---|---|
| `markdown` | 人間可読・一般的な AI | 中 |
| `xml` | 構造化データ向け AI | 中 |
| `plain` | シンプルなテキスト | 少 |

## Additional Resources

- **`references/repomix-config.md`** - repomix.config.json の完全リファレンス
- **`references/rtk-patterns.md`** - rtk のパイプパターン集
