# 並列化が有効なパターン集

## 並列化すべき処理の条件

並列実行が効果的なのは以下の条件が全て揃う場合:

1. 各コマンドが**互いに独立**している（入出力が依存しない）
2. 処理に**一定の時間**がかかる（I/O や計算コストがある）
3. 結果の**順序が重要でない**（または `--keep-order` で制御できる）

## よく使うパターン

### Lint・型チェック・テストの並列実行

```bash
# 独立したチェックを並列実行
rust-parallel ::: \
  "pnpm run lint" \
  "pnpm run typecheck" \
  "pnpm run test:unit" \
  "pnpm run test:e2e"

# 結果コードを確認
echo "Exit: $?"
```

### 複数パッケージの並列ビルド

```bash
# Monorepo の各パッケージを並列ビルド
ls -d packages/* | rust-parallel "cd {} && pnpm build"

# または
rust-parallel ::: \
  "cd packages/api && pnpm build" \
  "cd packages/web && pnpm build" \
  "cd packages/shared && pnpm build"
```

### ファイルリストの並列処理

```bash
# TypeScript ファイルを並列チェック
fd -e ts src/ | rust-parallel tsc --noEmit {}

# 複数ファイルに Semgrep を並列適用
fd -e ts -e tsx src/ | rust-parallel "semgrep --config auto {}"

# 画像ファイルを並列圧縮
fd -e png public/ | rust-parallel "convert {} -quality 85 {}"
```

### セキュリティスキャンの並列化

```bash
# 複数ツールを同時実行
rust-parallel ::: \
  "semgrep --config auto src/ 2>&1 | rtk" \
  "ghasec .github/workflows/ 2>&1" \
  "type-coverage 2>&1"
```

## 引数の組み合わせパターン

```bash
# 1対1マッピング（::: vs :::+）
rust-parallel echo ::: "a" "b" "c"
# → echo a, echo b, echo c

# 直積（::: vs :::）
rust-parallel echo ::: "env" "test" :::  "lint" "build"
# → echo env lint, echo env build, echo test lint, echo test build

# 1対1マッピング（同数の引数リスト）
rust-parallel echo ::: "file1.ts" "file2.ts" :::+ "out1.js" "out2.js"
# → echo file1.ts out1.js, echo file2.ts out2.js
```

## 出力の制御

```bash
# 出力を順序通りに（デフォルトは実行終了順）
rust-parallel --keep-order ::: "cmd1" "cmd2" "cmd3"

# 出力をグループ化（混在しない）
rust-parallel --group ::: "long-cmd-1" "long-cmd-2"

# 失敗しても継続
rust-parallel ::: "cmd1" "failing-cmd" "cmd3"
# デフォルトで失敗したコマンドがあっても継続する
```

## repomix の並列圧縮

大規模リポジトリを複数セクションに分けて並列処理:

```bash
# セクション別に並列生成
rust-parallel ::: \
  "repomix --include 'src/api/**' --output /tmp/ctx-api.md --style markdown" \
  "repomix --include 'src/ui/**' --output /tmp/ctx-ui.md --style markdown" \
  "repomix --include 'tests/**' --output /tmp/ctx-tests.md --style markdown"

# 結合
cat /tmp/ctx-api.md /tmp/ctx-ui.md /tmp/ctx-tests.md > CONTEXT.md
rm /tmp/ctx-*.md
```

## エラーハンドリング

```bash
# 失敗したコマンドを記録
rust-parallel ::: "cmd1" "cmd2" "cmd3" 2>&1 | tee parallel.log
FAILED=$(grep -c "failed" parallel.log || echo 0)
echo "Failed jobs: $FAILED"

# タイムアウト付き（長時間実行を防ぐ）
rust-parallel --timeout 60 ::: "long-cmd-1" "long-cmd-2"
```

## 並列化してはいけないパターン

```bash
# NG: 同じファイルへの書き込み（競合する）
rust-parallel ::: \
  "echo 'line1' >> output.txt" \
  "echo 'line2' >> output.txt"

# OK: 別ファイルへ書き込む
rust-parallel ::: \
  "echo 'line1' > /tmp/out1.txt" \
  "echo 'line2' > /tmp/out2.txt"
cat /tmp/out1.txt /tmp/out2.txt > output.txt

# NG: 依存関係がある処理（build → deploy）
rust-parallel ::: "pnpm build" "pnpm deploy"  # deploy は build 後でないと実行できない

# OK: 逐次実行
pnpm build && pnpm deploy
```
