# C2Lab 開発ガイド

## VCS

- このリポジトリでは **Jujutsu (jj)** を使用する。`git` コマンドではなく `jj` コマンドを使うこと
- ブランチ切り替え: `jj bookmark set` / `jj new` など jj のコマンドを使用する
- push: `jj git push` を使用する（safe-push skill 経由を推奨）

## プラグイン開発

### CI バリデーション

- `python scripts/validate-plugins.py` でローカル検証できる
- `plugins/**`, `.claude-plugin/marketplace.json`, `scripts/validate-plugins.py` の変更時に GitHub Actions で自動実行される

### ディレクトリ構造

- `.claude-plugin/` には `plugin.json` のみ配置する。`commands/`, `agents/`, `skills/`, `hooks/` はプラグインルート直下に置くこと
- 公式ドキュメント: https://code.claude.com/docs/en/plugins-reference

```
plugins/<plugin-name>/
├── .claude-plugin/
│   └── plugin.json           # マニフェスト (name が必須)
├── commands/                  # スキル Markdown (レガシー、新規は skills/ 推奨)
├── agents/                    # サブエージェント .md
├── skills/                    # <name>/SKILL.md 構造
├── hooks/
│   └── hooks.json             # フック設定
├── .mcp.json                  # MCP サーバー定義 (任意)
├── .lsp.json                  # LSP サーバー定義 (任意)
└── settings.json              # デフォルト設定 (任意)
```

### plugin.json

- `name` が唯一の必須フィールド。kebab-case (`^[a-z][a-z0-9]*(-[a-z0-9]+)*$`)
- `version` はセマンティックバージョニング (`X.Y.Z`)。marketplace.json でも指定可能で、plugin.json 側が優先
- コンポーネントパス (`commands`, `agents`, `skills`, `hooks`, `mcpServers`, `lspServers`, `outputStyles`) は `./` で始める。`../` は禁止
- カスタムパスはデフォルトディレクトリに **追加** される（置換ではない）
- `hooks` にデフォルトパス `./hooks/hooks.json` を指定しない（自動検出と重複する）
- `hooks`, `mcpServers`, `lspServers` は `string | array | object`（インライン設定可）

### hooks.json

- 有効なイベントタイプ: `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, `UserPromptSubmit`, `Notification`, `Stop`, `SubagentStart`, `SubagentStop`, `SessionStart`, `SessionEnd`, `TeammateIdle`, `TaskCompleted`, `PreCompact`
- フック type: `command`（シェル実行）, `prompt`（LLM 評価）, `agent`（エージェント検証）
- スクリプトパスには `${CLAUDE_PLUGIN_ROOT}` を使用する

### エージェント .md

- YAML フロントマターに `name` と `description` が必須

### SKILL.md

- `skills/<name>/SKILL.md` の構造で配置
- YAML フロントマターに `name` と `description` が必須

### marketplace.json

- 各プラグインの `source` パスが実在し、その先に `.claude-plugin/plugin.json` があること
