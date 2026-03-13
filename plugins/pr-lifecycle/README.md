# pr-lifecycle

PR ライフサイクル全体を管理するプラグイン。PR 作成・CI ローカル検証・レビュー対応・マージまでのワークフローを標準化する。

## 解決する問題

- push 後に CI が落ちて複数ラウンドの修正が発生する
- PR 作成時のタイトル・本文フォーマットがばらつく
- レビューコメントへの返信を忘れたり、plain コメントで返してしまう

## コンポーネント

### スキル: `pr-lifecycle`

PR ライフサイクル全体のワークフロー参照。以下の場面で自動的に読み込まれる:

- 「PR を作る」「CI チェック」「push する前に」「マージ準備」などと指示したとき
- `/pr-lifecycle:ci-check` や `/pr-lifecycle:open-pr` を実行したとき

### コマンド

| コマンド | 説明 |
|---------|------|
| `/pr-lifecycle:ci-check` | プロジェクトの CI（lint/format/型チェック/テスト）をローカル実行 |
| `/pr-lifecycle:open-pr` | 現在のブランチから規約に従った PR を作成 |

## 使い方

### push 前の CI 検証

```
/pr-lifecycle:ci-check
```

TypeScript・Python・Rust を自動検出して全 CI を実行。`--fix` オプションで format を自動修正。

```
/pr-lifecycle:ci-check --fix
```

### PR 作成

```
/pr-lifecycle:open-pr feat: ユーザー認証機能の追加
```

### レビュー対応

レビューコメントへの対応は [`review-workflow`](../review-workflow/README.md) プラグインを使用する。

## 他プラグインとの関係

| プラグイン | 役割 |
|-----------|------|
| `pr-lifecycle` (本プラグイン) | PR 作成・CI 検証・マージ準備 |
| `review-workflow` | PR レビューコメントへの対応（fix → commit → push → reply） |
| `jj-vcs-workflow` | jj を使った VCS 操作・safe-push |
| `code-review` | 他者の PR をレビューする |
