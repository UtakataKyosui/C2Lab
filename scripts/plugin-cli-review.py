#!/usr/bin/env python3
"""C2Lab プラグインの CLI ツール化候補を分析し、DevLab に Issue を作成する.

Claude Agent SDK（anthropic Python SDK のエージェントループ）を使用して、
.claude-plugin/marketplace.json と各プラグインの README・SKILL.md を読み込み、
スタンドアロン CLI ツールとして実装価値があるプラグインを特定する。
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import anthropic

REPO_ROOT = Path(__file__).resolve().parent.parent
DEVLAB_REPO = "UtakataKyosui/DevLab"
ISSUE_LABEL = "plugin-cli-upgrade"

SYSTEM_PROMPT = """\
You are a plugin-to-CLI migration analyst for C2Lab.
Analyze C2Lab plugins and identify those that could be implemented as standalone CLI tools.

CLI candidate criteria (score 7+ = candidate):
1. Works without Claude Code (pure computation, file transformation, static analysis, etc.)
2. Has a clear CLI interface (arguments, flags, stdin/stdout, exit codes)
3. Automates a specific development task
4. Composable with other tools via pipes

Not a candidate (score below 7):
- Pure guide/reference plugins (knowledge provision is the main purpose)
- Plugins that depend on Claude Code session management
- Plugins requiring external services as prerequisites (e.g., Obsidian Vault must exist)

Issue format:
- Title: [CLI化提案] {plugin_name} をスタンドアロン CLI ツールとして実装する
- Label: plugin-cli-upgrade
- Body sections: 概要 / CLI化の根拠 / 想定するCLIコンセプト / 使用例（code block） / 実装の方向性（checklist） / 自動生成フッター

Always include in footer:
*このIssueは [C2Lab plugin-cli-review](https://github.com/UtakataKyosui/C2Lab/actions/workflows/plugin-cli-review.yml) によって自動生成されました。*
"""

TOOLS: list[anthropic.types.ToolParam] = [
    {
        "name": "read_file",
        "description": "Read a file from the C2Lab repository by relative path.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "File path relative to repo root (e.g. '.claude-plugin/marketplace.json')",
                },
            },
            "required": ["path"],
        },
    },
    {
        "name": "glob_files",
        "description": "Find files matching a glob pattern within the C2Lab repository.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "Glob pattern relative to repo root (e.g. 'plugins/color-distance/skills/*/SKILL.md')",
                },
            },
            "required": ["pattern"],
        },
    },
    {
        "name": "gh_command",
        "description": (
            "Run a GitHub CLI (gh) command against UtakataKyosui/DevLab. "
            "Allowed subcommands: 'issue' and 'label'. "
            "Always include '--repo UtakataKyosui/DevLab' in args. "
            "GH_TOKEN is set automatically."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "args": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "gh command arguments (e.g. ['issue', 'list', '--repo', 'UtakataKyosui/DevLab', '--label', 'plugin-cli-upgrade', '--state', 'all', '--json', 'title,number'])",
                },
            },
            "required": ["args"],
        },
    },
]


def _read_file(path: str) -> dict[str, str]:
    target = (REPO_ROOT / path.lstrip("/")).resolve()
    if not target.is_relative_to(REPO_ROOT):
        return {"error": "Path traversal not allowed"}
    try:
        return {"content": target.read_text(encoding="utf-8")}
    except FileNotFoundError:
        return {"error": f"File not found: {path}"}
    except OSError as e:
        return {"error": str(e)}


def _glob_files(pattern: str) -> dict[str, list[str]]:
    matches = sorted(REPO_ROOT.glob(pattern))
    return {"files": [str(m.relative_to(REPO_ROOT)) for m in matches]}


def _gh_command(args: list[str]) -> dict[str, str | int]:
    if not args or args[0] not in {"issue", "label"}:
        return {"error": "Only 'issue' and 'label' gh subcommands are allowed"}
    devlab_token = os.environ.get("DEVLAB_GH_TOKEN", "")
    if not devlab_token:
        return {"error": "DEVLAB_GH_TOKEN is not set"}
    env = {**os.environ, "GH_TOKEN": devlab_token}
    try:
        result = subprocess.run(
            ["gh", *args],
            capture_output=True,
            text=True,
            env=env,
            timeout=30,
        )
    except subprocess.TimeoutExpired:
        return {"error": "gh command timed out"}
    return {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode,
    }


def _process_tool(name: str, tool_input: dict) -> str:  # type: ignore[type-arg]
    if name == "read_file":
        result = _read_file(tool_input["path"])
    elif name == "glob_files":
        result = _glob_files(tool_input["pattern"])
    elif name == "gh_command":
        result = _gh_command(tool_input["args"])
    else:
        result = {"error": f"Unknown tool: {name}"}
    return json.dumps(result, ensure_ascii=False)


def _build_prompt(dry_run: bool, max_issues: int) -> str:
    return f"""\
以下の手順で C2Lab プラグインを分析し、UtakataKyosui/DevLab に Issue を起票してください。

設定:
- DRY_RUN: {str(dry_run).lower()}  （true の場合、Issue を作成せずに候補一覧のみ出力）
- MAX_ISSUES: {max_issues}  （作成する Issue の上限数）

## 手順

### 1. プラグイン一覧の取得
read_file ツールで `.claude-plugin/marketplace.json` を読み込む。
plugins 配列の各エントリから name, source, description, keywords を把握する。

### 2. 各プラグインの詳細確認
各プラグインの source パス（例: "./plugins/color-distance"）について:
- read_file で `plugins/<name>/README.md` を読む（あれば）
- glob_files で `plugins/<name>/skills/*/SKILL.md` を検索し、見つかれば read_file で読む

### 3. CLI 候補の評価
各プラグインを score 1-10 で評価し、score 7 以上を候補とする。

### 4. 既存 Issue の確認（重複排除）
gh_command で既存の Issue タイトルを取得し、プラグイン名が含まれているものは除外する:
args: ["issue", "list", "--repo", "UtakataKyosui/DevLab", "--label", "plugin-cli-upgrade", "--state", "all", "--json", "title,number", "--limit", "100"]

### 5. ラベルの作成（なければ）
gh_command でラベルを作成する（既存の場合はエラーを無視する）:
args: ["label", "create", "plugin-cli-upgrade", "--repo", "UtakataKyosui/DevLab", "--color", "0075ca", "--description", "プラグインのCLIツール化提案"]

### 6. Dry run チェック
DRY_RUN が true の場合、Issue を作成せずに候補一覧（スコア、理由を含む）を出力して終了する。

### 7. Issue の作成（score 降順、最大 MAX_ISSUES 件）
各 Issue の本文を構成してから gh_command で作成する:
args: ["issue", "create", "--repo", "UtakataKyosui/DevLab", "--title", "...", "--body", "...", "--label", "plugin-cli-upgrade"]

### 8. 完了
作成した Issue の URL を出力して終了する。
"""


def main() -> None:
    """エージェントループのエントリーポイント."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("Error: ANTHROPIC_API_KEY is not set", file=sys.stderr)
        sys.exit(1)
    if not os.environ.get("DEVLAB_GH_TOKEN"):
        print("Error: DEVLAB_GH_TOKEN is not set", file=sys.stderr)
        sys.exit(1)

    dry_run = os.environ.get("DRY_RUN", "false").lower() == "true"
    max_issues = int(os.environ.get("MAX_ISSUES", "5"))

    client = anthropic.Anthropic()
    messages: list[anthropic.types.MessageParam] = [
        {"role": "user", "content": _build_prompt(dry_run, max_issues)},
    ]

    print(f"Starting plugin CLI review (dry_run={dry_run}, max_issues={max_issues})")

    # エージェントループ
    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=8192,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        # アシスタントのレスポンスを履歴に追加
        messages.append({"role": "assistant", "content": response.content})

        # テキスト出力
        for block in response.content:
            if hasattr(block, "text"):
                print(block.text)

        # 終了判定
        if response.stop_reason == "end_turn":
            break

        # ツール呼び出しの処理
        if response.stop_reason == "tool_use":
            tool_results: list[anthropic.types.ToolResultBlockParam] = []
            for block in response.content:
                if block.type == "tool_use":
                    short_input = json.dumps(block.input, ensure_ascii=False)[:120]
                    print(f"[tool] {block.name}({short_input})")
                    result_content = _process_tool(block.name, block.input)
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result_content,
                        }
                    )
            messages.append({"role": "user", "content": tool_results})
        else:
            # max_tokens 等による予期しない停止
            print(f"Unexpected stop_reason: {response.stop_reason}", file=sys.stderr)
            break


if __name__ == "__main__":
    main()
