#!/usr/bin/env bash
# SessionStart hook: otel-env.json から環境変数を読み込み、
# 動的な project.name を追加して JSON を出力する。
# otel-env.json が未生成の場合は setup.sh を自動実行する。
# フックスクリプトのため、エラー時も必ず exit 0 する。

PLUGIN_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OTEL_ENV_FILE="$PLUGIN_ROOT/infra/otel-env.json"

# otel-env.json がなければ setup.sh を実行
if [ ! -f "$OTEL_ENV_FILE" ]; then
  bash "$PLUGIN_ROOT/infra/setup.sh" >&2 || true
fi

# otel-env.json が存在しない場合はフォールバック（空 env）
if [ ! -f "$OTEL_ENV_FILE" ]; then
  echo '{"env": {}}'
  exit 0
fi

PROJECT_NAME="$(basename "$PWD")"

# otel-env.json を読み込み、project.name を追加して出力
OTEL_ENV_FILE="$OTEL_ENV_FILE" PROJECT_NAME="$PROJECT_NAME" python3 - << 'PY' || echo '{"env": {}}'
import json, sys, os

with open(os.environ['OTEL_ENV_FILE']) as f:
    env = json.load(f)

project_attr = 'project.name=' + os.environ['PROJECT_NAME']
existing_attrs = env.get('OTEL_RESOURCE_ATTRIBUTES')
if existing_attrs:
    env['OTEL_RESOURCE_ATTRIBUTES'] = existing_attrs + ',' + project_attr
else:
    env['OTEL_RESOURCE_ATTRIBUTES'] = project_attr

json.dump({'env': env}, sys.stdout)
PY
