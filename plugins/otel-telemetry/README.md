# otel-telemetry

Claude Code の OpenTelemetry テレメトリを自動設定するプラグイン。

## 概要

セッション開始時に OpenTelemetry のリソース属性（プロジェクト名等）を環境変数として設定する。otel-collector と OpenObserve を用いたテレメトリ収集インフラの起動・停止・状態確認を提供する。

## 提供コンポーネント

### Commands (Skills)

| コマンド | 引数 | 説明 |
|----------|------|------|
| `otel-infra` | `start` / `stop` / `status` | OpenTelemetry インフラ（otel-collector + OpenObserve）の起動・停止・状態確認 |

## 使い方

```
/otel-infra start    # インフラを起動
/otel-infra stop     # インフラを停止
/otel-infra status   # 稼働状態を確認
```

## フック

| イベント | 処理 |
|----------|------|
| `SessionStart` | `session-env.sh` を実行し、`OTEL_RESOURCE_ATTRIBUTES` に現在のプロジェクト名を設定する |
