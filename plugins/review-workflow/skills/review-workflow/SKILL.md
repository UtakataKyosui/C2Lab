---
name: review-workflow
description: >
  PR レビュー対応ワークフローの自動化スキル。レビューコメント取得・コード修正・検証・コミット・Push の一連の流れを Python オーケストレーターで制御する。
  以下の場合に使用: (1) PR レビューに対応するとき (2) 「レビュー対応」「レビューの修正」「review response」と指示されたとき
  (3) /respond-review で明示的に呼び出されたとき (4) レビューコメントに基づくコード修正が必要なとき
---

# PR レビュー対応ワークフロー

PR のレビューコメントを取得し、修正・検証・コミット・Push する一連のワークフローを自動化する。

## ワークフロー概要

```
1. VCS検出 → 2. レビュー取得 → 3. SubAgentで修正 → 4. 検証 → 5. コミット → 6. Push
```

## Python スクリプト

全スクリプトは `${CLAUDE_PLUGIN_ROOT}/scripts/` に配置されている。

### vcs.py - VCS 自動検出

`.jj` ディレクトリの有無で jj/git を判定する。

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/vcs.py [project_dir]
```

出力例:
```json
{"vcs_type": "jj", "root_dir": "/path/to/repo", "current_branch": "main"}
```

### review_fetcher.py - レビューコメント取得

gh CLI でインラインコメントとレビュー本文を取得し、スレッド単位にグループ化する。

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/review_fetcher.py <PR_URL_or_number>
```

PR 参照形式:
- フル URL: `https://github.com/owner/repo/pull/123`
- リポジトリ + 番号: `owner/repo#123`
- 番号のみ: `123`（カレントリポジトリを自動検出）

### verifier.py - 検証実行

`.claude/review-workflow.local.md` に定義された検証コマンドを順次実行する。

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/verifier.py [project_dir]
```

### committer.py - コミット整理

修正計画（fix-plan.json）に基づいてレビューコメント単位でコミットする。

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/committer.py /tmp/review-fix-plan.json [project_dir]
```

- jj: `jj split` + `jj describe` でコミット分割
- git: `git add` + `git commit` で個別コミット

### push.py - Push 情報取得

Push に必要な情報を出力する（実際の Push は行わない）。

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/push.py [project_dir]
```

- jj: `jj-safe-push` スキルの使用を推奨
- git: Push コマンドを出力し、ユーザー確認後に実行

## 設定ファイル

プロジェクトの `.claude/review-workflow.local.md` に検証コマンドを定義する。

```markdown
---
verify:
  typecheck: "npx tsc --noEmit"
  test: "npm test"
  lint: "npx eslint . --max-warnings 0"
---

## プロジェクト固有メモ

このプロジェクトではレビュー対応時に以下に注意:
- MSW モックの更新を忘れない
- Figma デザインとの整合性を確認する
```

YAML frontmatter の `verify` セクションがスクリプトから読み取られる。Markdown 本文はスキル参照用のメモとして使用可能。

## VCS 別の動作

| 操作 | jj | git |
|------|-----|-----|
| コミット | `jj split` + `jj describe` | `git add` + `git commit` |
| Push | `jj-safe-push` スキル経由 | ユーザー確認後に `git push` |
| ブランチ検出 | `jj log` bookmarks | `git branch --show-current` |

## fix-plan.json の形式

SubAgent が出力する修正計画:

```json
[
  {
    "thread_id": 123,
    "summary": "型アノテーションの修正",
    "files": ["src/components/UserCard.tsx"],
    "commit_message": "fix: correct type annotation for user prop"
  }
]
```

詳細は `references/fix-plan-format.md` を参照。
