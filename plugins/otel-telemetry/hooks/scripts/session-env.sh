#!/usr/bin/env bash
# SessionStart hook: otel-env.json から環境変数を読み込み、
# CLAUDE_ENV_FILE に export 文を追記して Claude Code セッションに反映する。
# otel-env.json が未生成の場合は setup.sh を自動実行する。
# フックスクリプトのため、エラー時も必ず exit 0 する。

PLUGIN_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OTEL_ENV_FILE="$PLUGIN_ROOT/infra/otel-env.json"

# otel-env.json がなければ setup.sh を実行
if [ ! -f "$OTEL_ENV_FILE" ]; then
  bash "$PLUGIN_ROOT/infra/setup.sh" >&2 || true
fi

# otel-env.json が存在しない場合はスキップ
if [ ! -f "$OTEL_ENV_FILE" ]; then
  echo '{}'
  exit 0
fi

# CLAUDE_ENV_FILE が設定されていなければ環境変数を注入できない
if [ -z "$CLAUDE_ENV_FILE" ]; then
  echo '{}'
  exit 0
fi

PROJECT_NAME="$(basename "$PWD")"

# otel-env.json を読み込み、project.name を追加して CLAUDE_ENV_FILE に書き込む
OTEL_ENV_FILE="$OTEL_ENV_FILE" PROJECT_NAME="$PROJECT_NAME" CLAUDE_ENV_FILE="$CLAUDE_ENV_FILE" python3 - << 'PY' || true
import json, os, re, shlex

with open(os.environ['OTEL_ENV_FILE']) as f:
    env = json.load(f)

project_attr = 'project.name=' + os.environ['PROJECT_NAME']
existing_attrs = env.get('OTEL_RESOURCE_ATTRIBUTES')
if existing_attrs:
    env['OTEL_RESOURCE_ATTRIBUTES'] = existing_attrs + ',' + project_attr
else:
    env['OTEL_RESOURCE_ATTRIBUTES'] = project_attr

_valid_key = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')
with open(os.environ['CLAUDE_ENV_FILE'], 'a') as f:
    for key, value in env.items():
        if _valid_key.match(key):
            f.write(f'export {key}={shlex.quote(str(value))}\n')
PY
echo '{}'
