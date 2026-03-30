#!/usr/bin/env python3
"""
PreToolUse hook: jj commit 前 Python lint チェック（Blocking）

Bash ツール使用前に実行され、コマンドが `jj commit` の場合に
変更された Python ファイルに対して ruff check + ruff format --check を実行する。

- jj commit 以外のコマンドはパススルー
- ruff が未インストールの場合はブロックしてインストール案内を表示
- lint 失敗時は exit 2 でブロック（stderr を Claude にフィードバック）
- Python ファイルの変更がない場合はパススルー
"""

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def read_input():
    try:
        return json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError, OSError, UnicodeDecodeError):
        return None


def is_jj_commit(command: str) -> bool:
    return bool(re.search(r"\bjj\s+commit\b", command))


def get_changed_python_files() -> list[str]:
    try:
        result = subprocess.run(
            ["jj", "diff", "--name-only"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return []
        files = result.stdout.strip().splitlines()
        return [f for f in files if f.endswith(".py") and Path(f).exists()]
    except (subprocess.TimeoutExpired, OSError):
        return []


def run_ruff(files: list[str]) -> tuple[bool, str]:
    errors = []

    check = subprocess.run(
        ["ruff", "check", *files],
        capture_output=True,
        text=True,
    )
    if check.returncode != 0:
        errors.append(check.stdout)

    fmt = subprocess.run(
        ["ruff", "format", "--check", *files],
        capture_output=True,
        text=True,
    )
    if fmt.returncode != 0:
        errors.append(fmt.stdout)

    if errors:
        return False, "\n".join(errors)
    return True, ""


def main():
    data = read_input()
    if not data:
        print("{}")
        return

    command = data.get("tool_input", {}).get("command", "")
    if not is_jj_commit(command):
        print("{}")
        return

    if shutil.which("ruff") is None:
        print(
            "[pre-commit-lint] ruff が見つかりません。brew install ruff でインストールしてください。",
            file=sys.stderr,
        )
        sys.exit(2)

    py_files = get_changed_python_files()
    if not py_files:
        print("{}")
        return

    ok, errors = run_ruff(py_files)
    if not ok:
        print(
            f"[pre-commit-lint] ruff チェック失敗。コミット前に修正してください:\n\n{errors}",
            file=sys.stderr,
        )
        sys.exit(2)

    print("{}")


if __name__ == "__main__":
    main()
