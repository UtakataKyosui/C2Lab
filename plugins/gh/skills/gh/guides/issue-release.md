# Issue & Release Management with gh

## Issue 管理

### Issue の作成

```bash
# 基本的な Issue 作成
gh issue create --title "バグ: ..." --body "..."

# 詳細オプション
gh issue create \
  --title "feat: ..." \
  --label "enhancement" \
  --assignee @me \
  --milestone "v2.0"

# HEREDOC でボディを書く
gh issue create --title "タイトル" --body "$(cat <<'EOF'
## 再現手順
1. ...

## 期待する動作
...
EOF
)"
```

### Issue の操作

```bash
# 一覧・検索
gh issue list                     # オープン Issue 一覧
gh issue list --label "bug"       # ラベルでフィルタ
gh issue list --assignee @me      # 自分にアサインされたもの
gh issue list --state closed      # クローズ済み

# 詳細表示
gh issue view <number>
gh issue view <number> --web      # ブラウザで開く

# 操作
gh issue close <number>
gh issue close <number> --comment "クローズ理由"
gh issue reopen <number>
gh issue edit <number> --title "新しいタイトル"
gh issue edit <number> --add-label "priority:high"
gh issue edit <number> --remove-label "needs-triage"
```

## リリース管理

### リリースの作成

```bash
# 基本的なリリース作成
gh release create v1.0.0

# 詳細オプション
gh release create v1.0.0 \
  --title "Release v1.0.0" \
  --notes "リリースノート" \
  --target main

# ファイルを添付
gh release create v1.0.0 ./dist/app-linux ./dist/app-macos

# プレリリース
gh release create v1.0.0-beta.1 --prerelease

# ドラフト
gh release create v1.0.0 --draft

# generate-notes で自動生成
gh release create v1.0.0 --generate-notes
```

### リリースの管理

```bash
gh release list                   # リリース一覧
gh release view v1.0.0            # 特定リリースの詳細
gh release edit v1.0.0 --notes "更新されたノート"
gh release delete v1.0.0          # リリースを削除
gh release download v1.0.0        # アセットをダウンロード
```

## GitHub Actions ワークフロー操作

```bash
# ワークフロー一覧
gh workflow list

# ワークフローを手動実行
gh workflow run <workflow-name>
gh workflow run <workflow-name> --field key=value

# 実行履歴の確認
gh run list
gh run list --workflow <workflow-name>
gh run view <run-id>
gh run view <run-id> --log

# ワークフローの有効化・無効化
gh workflow enable <workflow-name>
gh workflow disable <workflow-name>

# 実行のキャンセル・再実行
gh run cancel <run-id>
gh run rerun <run-id>
gh run rerun <run-id> --failed     # 失敗したジョブのみ再実行
```

## Gist 操作

```bash
gh gist create <file>             # Gist 作成
gh gist create <file> --public
gh gist list                      # 自分の Gist 一覧
gh gist view <id>
```
