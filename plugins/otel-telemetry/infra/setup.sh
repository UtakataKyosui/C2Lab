#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"
OTEL_ENV_FILE="$SCRIPT_DIR/otel-env.json"

# --- Docker 用 .env ---
if [ -f "$ENV_FILE" ]; then
  echo "[otel-telemetry] .env は既に存在します。スキップします。"
else
  USER_NAME="$(id -un)"
  USER_EMAIL="${USER_NAME}@localhost"
  PASSWORD="$(LC_ALL=C tr -dc 'A-Za-z0-9' < /dev/urandom | head -c 16 || true)"
  AUTH_HEADER="Basic $(printf '%s:%s' "$USER_EMAIL" "$PASSWORD" | base64)"

  cat > "$ENV_FILE" <<EOF
# OpenTelemetry Collector
OTELCOL_IMG=otel/opentelemetry-collector-contrib:0.103.0
OTELCOL_ARGS=

# OpenObserve
OPENOBSERVE_ROOT_USER_EMAIL=${USER_EMAIL}
OPENOBSERVE_ROOT_PASSWORD=${PASSWORD}
OPENOBSERVE_AUTH=${AUTH_HEADER}
EOF

  chmod 600 "$ENV_FILE"
  echo "[otel-telemetry] .env を生成しました"
  echo "[otel-telemetry] 認証情報は $ENV_FILE に保存されました"
fi

# --- Claude Code 用 otel-env.json ---
if [ -f "$OTEL_ENV_FILE" ]; then
  echo "[otel-telemetry] otel-env.json は既に存在します。スキップします。"
else
  cat > "$OTEL_ENV_FILE" <<'EOF'
{
  "CLAUDE_CODE_ENABLE_TELEMETRY": "1",
  "OTEL_METRICS_EXPORTER": "otlp,prometheus",
  "OTEL_LOGS_EXPORTER": "otlp",
  "OTEL_EXPORTER_OTLP_PROTOCOL": "grpc",
  "OTEL_EXPORTER_OTLP_ENDPOINT": "http://localhost:4317",
  "OTEL_METRIC_EXPORT_INTERVAL": "1000",
  "OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE": "delta",
  "OTEL_LOG_TOOL_DETAILS": "1",
  "OTEL_LOG_USER_PROMPTS": "1"
}
EOF

  echo "[otel-telemetry] otel-env.json を生成しました"
fi

echo "[otel-telemetry] セットアップ完了"
echo "  OpenObserve UI: http://localhost:5080"
