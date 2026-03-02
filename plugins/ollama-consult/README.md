# ollama-consult

ローカルLLM（Ollama）をClaudeの相談相手として活用し、計画・方針の壁打ちによる意思決定を支援するプラグインです。

軽量な問いかけをローカルLLMに委譲することで、Claude APIの利用を抑えながら意思決定のスピードを向上させます。

## 機能

- **`consult_local_llm`**: 計画・設計・アプローチ比較をローカルLLMに相談する
- **`list_models`**: 利用可能な Ollama モデルの一覧を表示する
- **`/ollama-consult:status`**: 接続確認と現在の設定を表示するコマンド

## 前提条件

- [Ollama](https://ollama.com) がインストール・起動済みであること
- Python 3.9 以上
- 使用したいモデルがプル済みであること（例: `ollama pull llama3.2`）

## セットアップ

### 1. Ollama を起動する

```bash
ollama serve
```

### 2. モデルをインストールする（未インストールの場合）

```bash
ollama pull llama3.2   # 軽量・高速（壁打ち用に推奨）
ollama pull gemma3     # 日本語性能が高い
```

### 3. 設定する

プロジェクトの `.claude/settings.local.json`（個人設定・gitignore済み）に追記します:

```json
{
  "env": {
    "OLLAMA_HOST": "http://localhost:11434",
    "OLLAMA_MODEL": "llama3.2"
  }
}
```

テンプレートとして `settings.local.json.example` が同梱されています。

設定後は Claude Code を再起動してください（MCP サーバーが環境変数を読み込むため）。

### 4. 接続を確認する

Claude Code で以下を実行:

```
/ollama-consult:status
```

## 設定オプション

`.claude/settings.local.json` の `env` セクションで設定します:

| 環境変数 | デフォルト | 説明 |
|---|---|---|
| `OLLAMA_HOST` | `http://localhost:11434` | Ollama サーバーの URL |
| `OLLAMA_MODEL` | （必須） | 使用するモデル名 |
| `OLLAMA_SYSTEM_PROMPT` | 英語のデフォルト | LLM へのシステムプロンプト（任意） |

## 使い方

Claude が自動的にローカルLLMを参照します。以下のような場面で活性化します:

- 「壁打ちしたい」「アプローチを比較したい」
- 「ローカルLLMに相談」「方針を確認したい」
- 実装方針を決める前のブレインストーミング

手動でも呼び出せます:

```
RedisとPostgreSQLのどちらをキャッシュに使うべきか、ローカルLLMで壁打ちして
```

## セキュリティ

- セキュリティに関わる情報（認証トークン、脆弱性分析など）はローカルLLMに送らないこと
- ローカルLLMの回答は参考意見として扱い、重要な決定は必ず検証すること

## .gitignore

`.claude/settings.local.json` は Claude Code がデフォルトで gitignore 対象としているため、
追加の設定は不要です。
