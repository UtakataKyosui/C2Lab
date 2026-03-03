---
name: vibe-kanban:setup
description: vibe-kanbanのインストール・初期設定・Claude Code連携を対話形式でガイドする
allowed-tools:
  - Bash
---

vibe-kanban の初期セットアップをステップバイステップでガイドしてください。

## Step 1: vibe-kanban のインストール確認

Bash ツールで `npx vibe-kanban --version 2>/dev/null || echo "NOT_INSTALLED"` を実行して確認してください。

- インストール済み（バージョン表示）: Step 2 へ進む
- 未インストール: 以下を案内する

```bash
# npx で即時実行（インストール不要）
npx vibe-kanban

# または npm でグローバルインストール
npm install -g vibe-kanban
vibe-kanban
```

## Step 2: 起動確認

Bash ツールで `curl -s -o /dev/null -w "%{http_code}" http://localhost:${VK_PORT:-3000} 2>/dev/null` を実行して確認してください。

- `200` または `301`: vibe-kanban が起動中 → Step 3 へ
- 接続失敗: 以下を案内する

```bash
# 新しいターミナルで実行
npx vibe-kanban
# または
vibe-kanban

# ブラウザが自動で開く。開かない場合は http://localhost:3000 にアクセス
```

## Step 3: Claude Code エージェント設定の確認

vibe-kanban で Claude Code を使うための設定手順を案内してください:

1. ブラウザで `http://localhost:3000` を開く
2. 右上の **Settings**（歯車アイコン）をクリック
3. **Agent Profiles** タブを選択
4. **Add Profile** → **Claude Code** を選択
5. 以下を設定:
   - **Model**: `claude-sonnet-4-5`（推奨）または `claude-opus-4-5`（複雑なタスク向け）
   - **Max Turns**: `50`（複雑なタスク向けに高めに設定）
   - **Working Directory**: プロジェクトのルートディレクトリ

## Step 4: プロジェクト（ワークスペース）の作成

1. vibe-kanban ホーム画面で **New Workspace** をクリック
2. git リポジトリのルートディレクトリを選択
3. ワークスペース名を入力（例: プロジェクト名）
4. **Create** をクリック

## Step 5: 最初のタスク作成

セットアップが完了したら、最初のタスクを作成するよう促してください:

1. **New Issue** ボタンをクリック
2. 明確なタイトルと説明を入力（詳細は `vibe-kanbanでタスク管理したい` でスキルを参照）
3. **Create** → **Start** でClaude Codeセッション開始

## トラブルシューティング

よくある問題があれば対応してください:

- **ポート 3000 が使用中**: `VK_PORT=3001 npx vibe-kanban` で別ポートを指定
- **Claude Code が認証エラー**: `~/.claude/credentials` ファイルの存在を確認。なければ `claude login` を実行
- **ワークスペースに git リポジトリが表示されない**: ディレクトリが `git init` 済みか確認 (`git status` で確認)

セットアップが完了したら、成功のサマリーを表示し、次のステップとして `vibe-kanbanでタスク管理したい` と入力して最適なワークフロースキルを読むよう案内してください。
