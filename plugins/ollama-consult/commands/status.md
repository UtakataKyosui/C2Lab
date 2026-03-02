---
name: ollama-consult:status
description: Ollamaの接続状態と利用可能なモデル一覧を確認する
allowed-tools:
  - mcp__plugin_ollama-consult_ollama-consult__list_models
  - Read
---

以下の手順で Ollama の接続状態を確認し、結果を表示してください。

1. `list_models` ツールを呼び出して Ollama の接続状態とモデル一覧を取得する
2. `.claude/settings.local.json` が存在する場合は Read ツールで内容を確認し、`env.OLLAMA_HOST` と `env.OLLAMA_MODEL` が設定されているかを表示する
3. 未設定の場合は、設定手順を案内する:

```
.claude/settings.local.json に以下を追加してください（既存の設定とマージ）:

{
  "env": {
    "OLLAMA_HOST": "http://localhost:11434",
    "OLLAMA_MODEL": "<list_models で表示されたモデル名>"
  }
}

設定後は Claude Code を再起動してください。
```

4. 接続できている場合: モデル一覧と現在の設定モデルを表示する
5. 接続できていない場合: `ollama serve` で Ollama を起動するよう案内する
