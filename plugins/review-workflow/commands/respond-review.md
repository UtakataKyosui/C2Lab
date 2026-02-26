---
name: respond-review
description: PR レビューコメントを取得し、修正・検証・コミット・Push までの一連のワークフローを実行する
argument-hint: "<PR URL or number>"
allowed-tools:
  - Bash
  - Read
  - Edit
  - Write
  - Glob
  - Grep
  - Task
  - Skill
  - AskUserQuestion
---

# PR レビュー対応ワークフロー

PR のレビューコメントを取得し、SubAgent で修正を実施、検証してコミット・Push する。

## 引数

- `$ARGUMENTS`: PR の URL（例: `https://github.com/owner/repo/pull/123`）または PR 番号

引数が未指定の場合は AskUserQuestion でユーザーに入力を求める。

**引数のバリデーション**: `$ARGUMENTS` は PR URL または数値のみを受け付ける。URL の場合は `https://github.com/` で始まること、番号の場合は数字のみであることを確認してから使用する。不正な入力はエラーとして拒否する。

## 実行手順

### Step 1: VCS 検出

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/vcs.py
```

出力の `vcs_type` を記録する（`jj` or `git`）。以降の手順で使用する。

### Step 2: レビューコメント取得

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/review_fetcher.py "$ARGUMENTS"
```

出力は JSON 形式で以下を含む:
- `pr`: PR のメタデータ（タイトル、ブランチ名等）
- `threads`: インラインコメントのスレッド一覧（`path`, `line`, `comments`）
- `review_bodies`: トップレベルのレビューコメント

### Step 3: レビュー内容の分析と修正計画

取得したレビューコメントを分析し、以下を特定する:
- 修正が必要なコメント（質問や議論のみのコメントは除外）
- 各コメントで求められている変更内容
- 影響するファイルとその箇所

修正が不要と判断した場合は、ユーザーに確認してからスキップする。

### Step 4: SubAgent でコード修正

Task ツールで `review-fixer` SubAgent を起動し、レビューコメントへの修正を実施する。

SubAgent に渡す情報:
- レビューコメントの内容（スレッド単位）
- 対象ファイルのパス
- プロジェクトのコンテキスト（CLAUDE.md の内容等）

SubAgent への指示:
- 各レビューコメントに対応するコード修正を実施する
- 修正完了後、修正内容を以下の JSON 形式で `/tmp/review-fix-plan-<PR番号>.json` に書き出す:

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

**重要**: SubAgent には修正の実装と fix-plan の出力のみを依頼する。検証やコミットは行わない。

### Step 5: 検証

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/verifier.py
```

検証に失敗した場合:
1. エラー内容を確認する
2. 修正が必要なら Step 4 に戻って再修正する（SubAgent を再起動）
3. 最大 3 回まで再試行する
4. 3 回失敗したらユーザーに報告して手動対応を求める

### Step 6: コミット

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/committer.py /tmp/review-fix-plan-<PR番号>.json
```

レビューコメント単位でコミットが作成される。

### Step 7: Push

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/push.py
```

出力に基づいて Push を実行する:

- **jj の場合**: `jj-safe-push` Skill を使用する
  ```
  /jj-safe-push
  ```

- **git の場合**: Push コマンドを表示し、AskUserQuestion でユーザーに確認を取ってから実行する
  ```
  AskUserQuestion: "以下のコマンドで Push してよいですか？ git push origin <branch>"
  ```

### Step 8: 完了報告

実行結果のサマリを表示する:
- 対応したレビューコメント数
- 作成したコミット数
- 検証結果
- Push 状態

## エラーハンドリング

- Python スクリプトが見つからない場合: `${CLAUDE_PLUGIN_ROOT}/scripts/` のパスを確認する
- gh CLI が認証されていない場合: `gh auth login` を案内する
- 設定ファイルが見つからない場合: `.claude/review-workflow.local.md` の作成を案内する
