---
name: アプリケーションセキュリティ（Semgrep / type-coverage / ghasec）
description: This skill should be used when the user asks to "セキュリティスキャン", "静的解析", use "Semgrep", "type-coverage", "ghasec", "脆弱性を検出", "TypeScript の型カバレッジ", "GitHub Actions のセキュリティ確認", or "アプリのセキュリティをチェック". Also activates when user asks about "SAST", "コードの脆弱性", "any 型の割合", or "GitHub Actions の設定ミス".
version: 0.1.0
---

# アプリケーションセキュリティ（Semgrep / type-coverage / ghasec）

3 つのツールでアプリケーション自体のセキュリティを多角的にチェックする：

- **Semgrep**: パターンベースの静的解析・セキュリティスキャン
- **type-coverage**: TypeScript コードの型カバレッジ（`any` 率）チェック
- **ghasec**: GitHub Actions ワークフローのセキュリティ解析

## Semgrep — 静的解析・セキュリティスキャン

### 基本使用法

```bash
# 言語を自動検出してスキャン（推奨）
semgrep --config auto <path>

# 特定ファイルをスキャン
semgrep --config auto src/api/users.ts

# カレントディレクトリ全体
semgrep --config auto .

# 特定のルールセットを使用
semgrep --config p/security-audit .
semgrep --config p/owasp-top-ten .
semgrep --config p/typescript .
```

### 出力形式

```bash
# テキスト（デフォルト）
semgrep --config auto .

# JSON 出力（CI 向け）
semgrep --config auto --json . > semgrep-results.json

# SARIF 形式（GitHub Security tab 向け）
semgrep --config auto --sarif . > semgrep.sarif

# 詳細度を抑える
semgrep --config auto --quiet .
```

### 誤検知の除外

```bash
# インラインで除外（1行）
const query = `SELECT * FROM users WHERE id = ${id}` // nosemgrep

# ファイル全体を除外
# semgrep: nosemgrep - legacy code, will be refactored

# .semgrepignore ファイルで除外
# node_modules/
# dist/
# *.test.ts
```

### CI での利用

```yaml
# .github/workflows/security.yml
- name: Run Semgrep
  uses: semgrep/semgrep-action@v1
  with:
    config: auto
    # または
    # config: p/security-audit
```

### PostToolUse Hook での使い方

Write/Edit 後に自動スキャンする場合:

```bash
#!/bin/bash
FILE="$1"
# サポートされる拡張子のみスキャン
case "$FILE" in
  *.ts|*.tsx|*.js|*.jsx|*.py|*.go|*.java|*.rb)
    semgrep --config auto "$FILE" 2>&1
    ;;
esac
```

## type-coverage — TypeScript 型カバレッジ

### 基本使用法

```bash
# 型カバレッジのパーセンテージを表示
type-coverage

# 詳細表示（any な箇所を表示）
type-coverage --detail

# 最低カバレッジを指定（達しなければ exit 1）
type-coverage --at-least 90

# strict モード（strictNullChecks 等も考慮）
type-coverage --strict

# カバレッジをキャッシュ
type-coverage --cache
```

### 出力例

```
97.5% (1234/1265)
```

97.5% の型が明示的に型付けされており、2.5% が `any` を含む。

### any を使っている箇所の確認

```bash
# any を使っている箇所を全て表示
type-coverage --detail 2>&1 | head -50

# any な箇所を JSON で出力
type-coverage --detail --json > type-coverage.json
```

### CI での利用

```bash
# 型カバレッジが 90% 未満なら失敗
type-coverage --at-least 90
```

### よくある any の原因と対処

| 原因 | 対処 |
|---|---|
| 外部ライブラリの型定義なし | `@types/<package>` をインストール |
| JSON.parse の結果 | `unknown` にして型ガードを使う |
| 動的なオブジェクト | `Record<string, unknown>` や interface を定義 |
| レガシーコード | 段階的に型付けして `@ts-ignore` を削除 |

## ghasec — GitHub Actions セキュリティ解析

### 基本使用法

```bash
# .github/workflows/ 配下を全てスキャン
ghasec

# 特定のワークフローファイルをスキャン
ghasec .github/workflows/ci.yml

# JSON 出力
ghasec --format json .

# 重要度でフィルタ（high 以上のみ）
ghasec --severity high
```

### 検出される問題例

```
CRITICAL: Use of pull_request_target with checkout of untrusted code
  File: .github/workflows/pr-check.yml
  Line: 15
  Reference: https://securitylab.github.com/research/github-actions-preventing-pwn-requests/

HIGH: Unpinned action version used
  File: .github/workflows/ci.yml
  Line: 8
  Detected: uses: actions/checkout@v4
  Recommendation: Pin to a specific commit SHA
```

### よく検出される問題と対処

| 問題 | 対処 |
|---|---|
| `pull_request_target` でコードをチェックアウト | `pull_request` を使うか、権限を制限する |
| アクションのバージョン未固定 | `@v4` → `@abc1234` のように SHA で固定 |
| `GITHUB_TOKEN` の過剰な権限 | `permissions` で最小権限を指定 |
| 環境変数でのシークレット漏洩 | `${{ secrets.X }}` を直接 `env:` に渡さない |
| `workflow_run` での信頼されないコードの実行 | トリガー条件を慎重に設定 |

### CI 統合

```yaml
# .github/workflows/security.yml
- name: Run ghasec
  run: |
    go install github.com/koki-develop/ghasec@latest
    ghasec .github/workflows/
```

## 3 ツールの使い分け

| 用途 | ツール |
|---|---|
| JS/TS/Python 等のコード脆弱性 | Semgrep |
| TypeScript の型安全性の維持 | type-coverage |
| GitHub Actions のセキュリティ設定ミス | ghasec |

## セキュリティスキャン実行フロー

```bash
# 1. コードの脆弱性スキャン
semgrep --config auto src/

# 2. TypeScript 型カバレッジ確認
type-coverage --at-least 90

# 3. GitHub Actions の設定確認
ghasec .github/workflows/

# 4. 結果を確認してリスクの高い問題から修正
```

## Additional Resources

- **`references/semgrep-rules.md`** - 推奨 Semgrep ルールセット一覧
- **`references/ghasec-vulnerabilities.md`** - GitHub Actions の典型的な脆弱性パターン
