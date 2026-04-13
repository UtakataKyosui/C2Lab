# 推奨 Semgrep ルールセット一覧

## 公式ルールセット

### 汎用セキュリティ

| ルールセット | 用途 | コマンド |
|---|---|---|
| `auto` | 言語自動検出で最適なルールを適用 | `semgrep --config auto` |
| `p/security-audit` | 包括的なセキュリティ監査 | `semgrep --config p/security-audit` |
| `p/owasp-top-ten` | OWASP Top 10 対応 | `semgrep --config p/owasp-top-ten` |
| `p/cwe-top-25` | CWE Top 25 対応 | `semgrep --config p/cwe-top-25` |

### 言語別ルールセット

| ルールセット | 対象言語 | コマンド |
|---|---|---|
| `p/typescript` | TypeScript | `semgrep --config p/typescript` |
| `p/javascript` | JavaScript | `semgrep --config p/javascript` |
| `p/python` | Python | `semgrep --config p/python` |
| `p/golang` | Go | `semgrep --config p/golang` |
| `p/java` | Java | `semgrep --config p/java` |

### フレームワーク別

| ルールセット | 対象 | コマンド |
|---|---|---|
| `p/react` | React | `semgrep --config p/react` |
| `p/nextjs` | Next.js | `semgrep --config p/nextjs` |
| `p/express` | Express.js | `semgrep --config p/express` |
| `p/django` | Django | `semgrep --config p/django` |

## カスタムルールの書き方

```yaml
# .semgrep.yml
rules:
  - id: no-console-log-in-prod
    patterns:
      - pattern: console.log(...)
    message: |
      console.log を本番コードで使用しています。
      ロガーライブラリを使用してください。
    languages: [typescript, javascript]
    severity: WARNING
    paths:
      exclude:
        - "*.test.ts"
        - "*.spec.ts"
        - "*.test.js"

  - id: no-any-cast
    pattern: $X as any
    message: "any へのキャストは型安全性を損ないます。適切な型を使用してください。"
    languages: [typescript]
    severity: WARNING

  - id: sql-injection-risk
    patterns:
      - pattern: |
          `SELECT ${...}`
      - pattern: |
          `INSERT ${...}`
      - pattern: |
          `UPDATE ${...}`
    message: "SQL 文字列に変数が直接埋め込まれています。パラメータ化クエリを使用してください。"
    languages: [typescript, javascript]
    severity: ERROR
```

## よく検出される脆弱性パターン

### XSS (Cross-Site Scripting)

```yaml
# dangerouslySetInnerHTML の検出
- id: react-dangerously-set-inner-html
  pattern: dangerouslySetInnerHTML={{__html: $X}}
  severity: ERROR
```

### Path Traversal

```yaml
- id: path-traversal
  patterns:
    - pattern: path.join($BASE, $USER_INPUT)
    - pattern: fs.readFile($USER_INPUT, ...)
  severity: ERROR
```

### 認証バイパス

```yaml
- id: jwt-none-algorithm
  pattern: jwt.sign($PAYLOAD, $SECRET, {algorithm: "none"})
  severity: CRITICAL
```

## Semgrep の出力を解釈する

```
/path/to/file.ts:42: [ERROR] rule-id
  42: const dangerous = eval(userInput)  // ← 問題のある行
      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  Note: eval() is dangerous...
```

- **ファイルパス:行番号**: 問題の場所
- **[SEVERITY] rule-id**: 重要度とルール名
- **Note**: 説明と修正方針

## 誤検知の制御

```typescript
// nosemgrep: rule-id  ← 1行を除外
const x = eval("safe code") // nosemgrep

// nosemgrep  ← 全ルールを除外
const legacy = dangerousFunction() // nosemgrep
```

```text
# .semgrepignore
# 特定ディレクトリを除外
tests/fixtures/
src/generated/
node_modules/
```
