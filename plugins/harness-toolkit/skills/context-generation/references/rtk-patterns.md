# rtk パイプパターン集

## 基本パターン

`rtk` はパイプで受け取った stdout テキストを AI 向けに意味を保ったまま圧縮する。

```bash
# 基本的な使い方
<command> | rtk

# ファイルに書き出しながら圧縮
<command> | rtk > output.txt

# 複数コマンドの組み合わせ
<command1> | <command2> | rtk
```

## ツール出力への適用

```bash
# ripgrep の出力を圧縮
rg 'pattern' | rtk

# fd の出力を圧縮
fd -e ts | rtk

# Semgrep の結果を圧縮
semgrep --config auto . 2>&1 | rtk

# git log を圧縮
git log --oneline -50 | rtk

# jj log を圧縮
jj log --no-pager | rtk

# npm ls の出力を圧縮
npm ls --depth=3 | rtk

# tree/tre の出力を圧縮
tre | rtk
```

## repomix との組み合わせ

```bash
# repomix の出力を直接 rtk に渡す
repomix --output /dev/stdout --style plain | rtk > CONTEXT.md

# より詳細な制御
repomix --include "src/**" --output /dev/stdout | rtk > CONTEXT_COMPACT.md
```

## Hook スクリプトでの rtk 使用

rtk が利用可能な場合のみ使うパターン:

```bash
#!/bin/bash
run_with_rtk() {
  if command -v rtk &>/dev/null; then
    "$@" | rtk
  else
    "$@"
  fi
}

# 使用例
run_with_rtk rg 'pattern'
run_with_rtk semgrep --config auto src/
run_with_rtk jj log --no-pager
```

## インライン条件付き適用

```bash
# 1行でチェックしてパイプ
rg 'pattern' | { command -v rtk &>/dev/null && rtk || cat; }

# bash 変数を使う
RTK=$(command -v rtk 2>/dev/null || echo "cat")
rg 'pattern' | $RTK
```

## 大きな出力の圧縮

rtk が最も効果を発揮するケース:

```bash
# 長い diff を圧縮
jj diff | rtk

# 詳細ログを圧縮
pnpm install --verbose 2>&1 | rtk

# テスト結果を圧縮
pnpm test 2>&1 | rtk

# TypeScript エラーを圧縮
tsc --noEmit 2>&1 | rtk

# Knip の未使用コード一覧を圧縮
knip 2>&1 | rtk
```

## 注意事項

- rtk はテキストを圧縮するため、厳密な行番号や正確なフォーマットが必要な場合は使わない
- 圧縮前のオリジナル出力が必要な場合は `tee` で保存する:
  ```bash
  semgrep --config auto . 2>&1 | tee semgrep-full.txt | rtk
  ```
- バイナリ出力や JSON 出力には使用しない（構造が壊れる場合がある）
