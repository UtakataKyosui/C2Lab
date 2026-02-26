---
name: otel-infra
description: OpenTelemetry インフラ (otel-collector + OpenObserve) の起動・停止・状態確認
arguments:
  - name: action
    description: "実行するアクション: start, stop, status"
    required: true
---

# OpenTelemetry インフラ管理

`${CLAUDE_PLUGIN_ROOT}/infra/` にある docker-compose でインフラを管理する。

## 手順

1. 引数 `$ARGUMENTS.action` を検証する:
   - 有効な値: `start`, `stop`, `status`
   - 無効な値の場合はエラーメッセージを表示して終了する

2. 検証済みの `$ARGUMENTS.action` に応じて以下を実行する:

### start
- `${CLAUDE_PLUGIN_ROOT}/infra/.env` が存在しなければ `bash "${CLAUDE_PLUGIN_ROOT}/infra/setup.sh"` を実行して生成する
- `docker compose -f "${CLAUDE_PLUGIN_ROOT}/infra/docker-compose.yaml" --env-file "${CLAUDE_PLUGIN_ROOT}/infra/.env" up -d` で起動
- 起動後に `docker compose -f "${CLAUDE_PLUGIN_ROOT}/infra/docker-compose.yaml" ps` で状態を表示
- OpenObserve UI: http://localhost:5080 を案内

### stop
- `docker compose -f "${CLAUDE_PLUGIN_ROOT}/infra/docker-compose.yaml" down` で停止

### status
- `docker compose -f "${CLAUDE_PLUGIN_ROOT}/infra/docker-compose.yaml" ps` で状態を表示

3. 結果をユーザーに報告する
