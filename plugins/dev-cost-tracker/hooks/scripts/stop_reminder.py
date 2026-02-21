#!/usr/bin/env python3
"""
Stop hook: コスト記録リマインダー

セッション終了時に、そのセッションのコストが .dev-costs.json に
記録されているかチェックし、未記録ならリマインダーを表示する。

- 常に exit 0（絶対にブロックしない）
- 外部依存なし（stdlib のみ）
"""

import json
import os
import sys

COSTS_FILE = ".dev-costs.json"


def read_input():
    """stdin から Stop hook の JSON データを読み取る"""
    try:
        return json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError, ValueError):
        return None


def is_session_tracked(cwd, session_id):
    """cwd/.dev-costs.json にセッションIDが記録済みかチェックする"""
    file_path = os.path.join(cwd, COSTS_FILE)
    try:
        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
        records = data.get("records", [])
        return any(r.get("session_id") == session_id for r in records)
    except (OSError, json.JSONDecodeError, ValueError):
        return False


def main():
    try:
        data = read_input()
        if not data:
            sys.exit(0)

        session_id = data.get("session_id")
        cwd = data.get("cwd")

        if not session_id or not cwd:
            sys.exit(0)

        if not is_session_tracked(cwd, session_id):
            print(
                "[dev-cost-tracker] このセッションのコストが未記録です。"
                " /record-cost でコスト情報を記録してください。",
                file=sys.stderr,
            )

    except Exception as e:
        # 何があっても絶対にブロックしない
        print(
            f"[dev-cost-tracker] 予期しないエラー: {e}",
            file=sys.stderr,
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
