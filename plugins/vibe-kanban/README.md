# vibe-kanban Plugin for Claude Code

Claude Code と [vibe-kanban](https://vibekanban.com) を連携させ、AI エージェントのタスク管理を最適化するプラグインです。

## 概要

vibe-kanban はローカルファーストのカンバンボードで、Claude Code・Codex・Gemini CLI などの AI コーディングエージェントをオーケストレーションするために設計されています。このプラグインにより、Claude Code セッションと vibe-kanban のカンバンボードをシームレスに連携できます。

## 機能

- **MCP 統合**: `npx vibe-kanban@latest --mcp` でタスク管理ツールを Claude Code から直接呼び出せる
- **ワークフロースキル**: Claude Code + vibe-kanban の最適なタスク管理手法を習得できる
- **セットアップコマンド**: インストールから初期設定まで対話形式でガイド
- **ブラウザ起動コマンド**: コマンドラインからカンバンボードを即座に開く
- **セッションフック**: 作業開始・終了時にタスク状態の更新を自動でリマインド

## インストール

```bash
# C2Lab マーケットプレイス経由でインストール
cc --plugin-dir /path/to/C2Lab/plugins/vibe-kanban
```

または `.claude/settings.json` に追加:

```json
{
  "plugins": ["/path/to/C2Lab/plugins/vibe-kanban"]
}
```

## 前提条件

- [vibe-kanban](https://github.com/BloopAI/vibe-kanban) が利用可能（`npx vibe-kanban` で起動可能）
- Node.js 18 以上

## 使い方

### 初期セットアップ

```
/vibe-kanban:setup
```

vibe-kanban のインストール・起動・Claude Code エージェント設定をステップバイステップでガイドします。

### カンバンボードを開く

```
/vibe-kanban:open
```

ブラウザで `http://localhost:3000` を開きます。vibe-kanban が起動していない場合は起動方法を案内します。

### ワークフロースキル

以下のフレーズで最適なワークフロー指導スキルが自動で読み込まれます:

- 「vibe-kanbanでタスク管理したい」
- 「Claude Codeとvibe-kanbanを連携させたい」
- 「vibe-kanbanのワークフローを教えて」
- 「AIエージェントのタスク設計のベストプラクティス」
- 「並列でClaude Codeを使いたい」

### セッションフック

**SessionStart**: Claude Code 起動時に vibe-kanban の接続状態を確認し、カンバンボードのURLを表示します。

**Stop**: セッション終了時に vibe-kanban でのタスクステータス更新を促します。

## ワークフロー概要

```
1. vibe-kanban でイシューを作成（明確なタイトルと受け入れ基準）
     ↓
2. 「Start」でClaude Codeセッションを開始（git worktree が自動作成）
     ↓
3. Claude Code が自律的に作業（コード変更、テスト実行）
     ↓
4. セッション完了後、vibe-kanban でdiffをレビュー
     ↓
5. 問題なければ「Create PR」でプルリクエスト作成
```

## リファレンス

スキルには以下の参考資料が含まれています:

- **タスク設計パターン**: 効果的なイシューテンプレートとアンチパターン
- **並列ワークフロー戦略**: 複数セッションを安全に並列実行する方法
- **MCP 設定ガイド**: vibe-kanban 経由での MCP サーバー設定

## 関連リンク

- [vibe-kanban 公式サイト](https://vibekanban.com)
- [vibe-kanban GitHub](https://github.com/BloopAI/vibe-kanban)
- [vibe-kanban ドキュメント](https://vibekanban.com/docs)
