---
name: 並列実行（rust-parallel）
description: This skill should be used when the user wants to "コマンドを並列実行", use "rust-parallel", "複数のコマンドを同時に実行", "並列処理でビルドを高速化", or wants to run independent commands concurrently. Also activates when user asks about "GNU parallel の代替", "コマンドの並列化", or "独立したタスクを並行処理".
version: 0.1.0
---

# 並列実行（rust-parallel）

`rust-parallel` は GNU parallel の Rust 実装。複数の独立したコマンドを並列実行することで、最終的な結果を得るまでの時間を大幅に短縮する。

## 基本使用法

### コマンドを並列実行

```bash
# コマンドを並列実行（標準入力から）
echo -e "cmd1\ncmd2\ncmd3" | rust-parallel

# ファイルからコマンドを読み込んで並列実行
cat commands.txt | rust-parallel

# 直接コマンドを指定
rust-parallel ::: "cmd1" "cmd2" "cmd3"
```

### ジョブ数の制御

```bash
# 最大並列数を指定（デフォルト: CPU コア数）
rust-parallel -j 4 ::: "cmd1" "cmd2" "cmd3"

# CPU コア数の 2 倍で実行
rust-parallel -j 200% ::: "cmd1" "cmd2" "cmd3"

# 順次実行（デバッグ用）
rust-parallel -j 1 ::: "cmd1" "cmd2" "cmd3"
```

### 引数の組み合わせ

```bash
# 各引数にコマンドを適用
rust-parallel echo ::: "hello" "world" "foo"
# → echo hello, echo world, echo foo を並列実行

# 2 つの引数リストの直積
rust-parallel echo ::: "a" "b" :::+ "1" "2"
# → echo a 1, echo a 2, echo b 1, echo b 2

# ファイルリストを処理
fd -e ts | rust-parallel tsc --noEmit {}
```

## よく使うパターン

### 複数のリント・テストを並列実行

```bash
# 独立したチェックを並列実行
rust-parallel ::: \
  "pnpm run lint" \
  "pnpm run typecheck" \
  "pnpm run test:unit"
```

### 複数ファイルの並列処理

```bash
# TypeScript ファイルを並列でコンパイル
fd -e ts src/ | rust-parallel tsc --noEmit {}

# 複数ファイルに Semgrep を並列適用
fd -e ts src/ | rust-parallel semgrep --config auto {}

# 複数ディレクトリに対してコマンドを並列実行
echo -e "packages/a\npackages/b\npackages/c" | rust-parallel "cd {} && pnpm build"
```

### Hook スクリプト内での活用

```bash
#!/bin/bash
# SessionStart hook: 複数ツールの存在確認を並列実行
TOOLS="fd rg jj repomix rtk semgrep rust-parallel"

check_tool() {
  tool="$1"
  if ! command -v "$tool" &>/dev/null; then
    echo "MISSING: $tool"
  fi
}

export -f check_tool
echo "$TOOLS" | tr ' ' '\n' | rust-parallel check_tool {}
```

### repomix + rtk を並列セクション処理

```bash
# 大きなリポジトリを複数セクションに分けて並列圧縮
rust-parallel ::: \
  "repomix --include 'src/api/**' --output /tmp/ctx-api.md" \
  "repomix --include 'src/ui/**' --output /tmp/ctx-ui.md" \
  "repomix --include 'tests/**' --output /tmp/ctx-tests.md"

# 結果を結合
cat /tmp/ctx-*.md > CONTEXT.md
```

## GNU parallel との比較

| 機能 | GNU parallel | rust-parallel |
|---|---|---|
| 実行速度 | 速い | より高速（Rust 製） |
| インストール | brew install parallel | cargo install rust-parallel |
| 構文 | `parallel` | `rust-parallel` |
| ::: 構文 | ✅ | ✅ |
| `{}` プレースホルダー | ✅ | ✅ |
| 進捗表示 | `--progress` | 同様 |
| クロスプラットフォーム | macOS/Linux | macOS/Linux/Windows |

## タイムアウトと失敗処理

```bash
# タイムアウトを設定（秒）
rust-parallel --timeout 30 ::: "cmd1" "cmd2"

# エラーが発生しても継続
rust-parallel --keep-order ::: "cmd1" "cmd2 && exit 1" "cmd3"

# 失敗したコマンドを記録
rust-parallel ::: "cmd1" "cmd2" 2>&1 | tee parallel.log
```

## 出力の制御

```bash
# 出力をグループ化（混在を防ぐ）
rust-parallel --group ::: "long-cmd-1" "long-cmd-2"

# 実行順序を維持して出力
rust-parallel --keep-order ::: "cmd1" "cmd2" "cmd3"

# サイレントモード（エラーのみ表示）
rust-parallel --quiet ::: "cmd1" "cmd2"
```

## 注意事項

- 並列実行するコマンドは互いに**独立している**必要がある
- ファイルへの同時書き込みは競合するため、出力ファイルを分けるか直列処理にする
- リソースを大量消費するコマンドは `-j` で並列数を制限する
- 副作用のあるコマンド（DB 書き込み等）は並列化の前に依存関係を確認する

## Additional Resources

- **`references/parallel-patterns.md`** - 並列化が有効なパターン集
