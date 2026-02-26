# fix-plan.json フォーマット仕様

## 概要

`fix-plan.json` は SubAgent（review-fixer）が修正結果を呼び出し元に伝えるための中間ファイル。
レビューコメント単位でのコミット整理に使用される。

## スキーマ

```json
[
  {
    "thread_id": number,
    "summary": string,
    "files": string[],
    "commit_message": string
  }
]
```

## フィールド詳細

### thread_id (required)
- レビュースレッドの ID（review_fetcher.py の出力と対応）
- 同一スレッドに対する複数修正がある場合、1エントリにまとめる

### summary (required)
- 修正内容の要約（日本語可）
- ユーザーへの報告に使用される
- **注意**: `commit_message` が未指定の場合にフォールバックとして使用されるため、その場合は英語で記述すること

### files (required)
- 変更したファイルのパス一覧（プロジェクトルートからの相対パス）
- committer.py がこの一覧を元に `jj split` / `git add` する

### commit_message (required)
- Conventional Commits 形式のコミットメッセージ
- 英語で記述する
- prefix: `fix:`, `refactor:`, `style:`, `test:`, `docs:`

## 例

### 単一ファイルの修正

```json
[
  {
    "thread_id": 2856474926,
    "summary": "VitalMetric コンポーネントのプロップ型を修正",
    "files": ["apps/dashboard/src/features/monitoring/components/vital-metric.tsx"],
    "commit_message": "fix: correct VitalMetric prop types for shared usage"
  }
]
```

### 複数ファイルにまたがる修正

```json
[
  {
    "thread_id": 2856474930,
    "summary": "モックハンドラーとテストデータの整合性修正",
    "files": [
      "apps/dashboard/src/mocks/handlers/vitals.ts",
      "apps/dashboard/__tests__/features/monitoring/vital-metric.test.tsx"
    ],
    "commit_message": "fix: align mock handler responses with updated type definitions"
  }
]
```

### 修正不要のコメントをスキップ

修正が不要と判断したレビューコメント（質問、確認、議論のみ）は fix-plan.json に含めない。
スキップした理由は SubAgent の出力メッセージで報告する。
