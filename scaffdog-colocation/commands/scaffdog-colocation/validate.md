---
description: プロジェクトのファイル構造がコロケーションパターンに準拠しているか検証し、違反レポートを生成する。
---

# scaffdog-colocation: validate

プロジェクト全体のコロケーションパターン準拠を検証します。

## 手順

### 1. 検証対象ディレクトリの特定

以下のディレクトリを検証対象とする:

- `src/components/`
- `src/features/`
- `src/pages/` / `src/app/`（Next.js App Router は除外）
- `src/hooks/`
- `src/lib/components/`（SvelteKit）

存在するディレクトリのみを対象にする。

### 2. colocation-validator エージェント呼び出し

`colocation-validator` エージェントを呼び出し、以下の検証を実行する:

#### 検証ルール

| ルール | Severity | 説明 |
|---|---|---|
| barrel-missing | error | `index.ts` が存在しない |
| naming-mismatch | warning | ファイル名がディレクトリ名と一致しない |
| test-missing | info | テストファイルが存在しない |
| types-inline | info | 型定義が分離されていない |
| deep-nesting | warning | 3階層以上のネスト |
| empty-directory | warning | 空のディレクトリが存在 |

### 3. レポート生成

違反を Markdown テーブルで表示:

```
## コロケーション検証レポート

検証対象: src/components/, src/features/

### 違反一覧

| Severity | Path | Rule | 説明 |
|---|---|---|---|
| error | src/components/Button/ | barrel-missing | index.ts がありません |
| warning | src/components/card/ | naming-mismatch | ディレクトリ名が PascalCase ではありません |
| info | src/components/Modal/ | test-missing | テストファイルがありません |

### サマリー

- error: 1 件
- warning: 1 件
- info: 1 件
- 検証済みディレクトリ: 15
```

### 4. 修正提案

各違反に対して具体的な修正方法を提案する:

- `barrel-missing`: `index.ts` の内容を生成して提案
- `naming-mismatch`: 正しい名前を提案
- `test-missing`: テストファイルのスケルトンを提案
- `deep-nesting`: リファクタリング方法を提案

**注意**: 自動修正は行わない。ユーザーに提案のみ行い、承認を得てから修正する。
