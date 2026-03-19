# PR Workflow with gh

## PR の作成

```bash
# 基本的な PR 作成
gh pr create --title "feat: add feature" --body "..."

# テンプレートを使用
gh pr create --fill               # コミットメッセージから自動生成
gh pr create --draft              # ドラフト PR として作成
gh pr create --base main          # ベースブランチを指定
gh pr create --assignee @me       # 自分にアサイン
gh pr create --label "bug,enhancement"

# HEREDOC でボディを書く
gh pr create --title "タイトル" --body "$(cat <<'EOF'
## Summary
- 変更内容

## Test plan
- [ ] テスト項目
EOF
)"
```

## PR の確認・レビュー

```bash
# 一覧表示
gh pr list                        # オープンな PR 一覧
gh pr list --author @me           # 自分の PR のみ
gh pr list --reviewer @me         # レビュー待ちの PR

# 詳細表示
gh pr view <number>               # PR の詳細
gh pr view <number> --web         # ブラウザで開く
gh pr diff <number>               # diff を表示

# レビュー操作
gh pr review <number> --approve   # 承認
gh pr review <number> --request-changes --body "コメント"
gh pr review <number> --comment --body "コメント"
```

## CI ステータスの確認

```bash
# PR に紐づく CI の確認
gh pr checks <number>             # チェックの一覧と状態
gh pr checks <number> --watch     # リアルタイムで監視

# ワークフロー実行の確認
gh run list --branch <branch>
gh run view <run-id>
gh run view <run-id> --log        # ログを表示
gh run watch <run-id>             # 完了まで待機
```

## PR のマージ

```bash
gh pr merge <number>              # インタラクティブにマージ方法を選択
gh pr merge <number> --merge      # merge commit
gh pr merge <number> --squash     # squash and merge
gh pr merge <number> --rebase     # rebase and merge
gh pr merge <number> --delete-branch  # マージ後にブランチ削除
```

## レビューコメントへの返信

PR コメントへの返信は GitHub Web UI または `gh` の API 経由で行います。

```bash
# コメント一覧の確認
gh pr view <number> --comments

# API 経由でコメントに返信
gh api repos/{owner}/{repo}/pulls/<number>/comments
```

## PR のクローズ・再オープン

```bash
gh pr close <number>
gh pr close <number> --comment "クローズ理由"
gh pr reopen <number>
```
