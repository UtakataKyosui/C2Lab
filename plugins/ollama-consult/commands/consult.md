---
name: ollama-consult:consult
description: ローカルLLM（Ollama）に質問・相談する
argument-hint: "<質問内容>"
allowed-tools:
  - mcp__plugin_ollama-consult_ollama-consult__consult_local_llm
  - mcp__plugin_ollama-consult_ollama-consult__list_models
---

ローカルLLM（Ollama）に相談します。

## 入力

引数: `$ARGUMENTS`

## 手順

1. `$ARGUMENTS` が空の場合は「質問内容を引数として渡してください。例: `/ollama-consult:consult Redis vs in-memory キャッシュの比較`」と案内して終了する

2. `consult_local_llm` を呼び出す:
   - `question`: `$ARGUMENTS` をそのまま渡す
   - `context`: 現在の会話コンテキストから関連する背景情報があれば付与する（なければ省略）

3. 得られた回答を表示する。表示時は以下の形式にする:

   ```
   ## ローカルLLMの回答

   <回答内容>

   ---
   *この回答はローカルLLM（Ollama）によるものです。重要な判断は必ず検証してください。*
   ```

4. 接続エラーの場合は `/ollama-consult:status` で接続状態を確認するよう案内する
