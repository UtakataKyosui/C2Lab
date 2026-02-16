#!/usr/bin/env python3
"""
UserPromptSubmit hook: セッションID自動保存

プロンプト送信時にセッションIDを取得し、プロジェクトルートの
.claude-sessions.json に追記する。重複チェックにより同一セッション内では
1回だけ記録される。

- 常に exit 0（絶対にブロックしない）
- 外部依存なし（stdlib のみ）
"""

import json
import os
import sys
from datetime import datetime, timezone

MAX_HISTORY = 100
SESSIONS_FILE = ".claude-sessions.json"


def read_input():
    """stdin から UserPromptSubmit の JSON データを読み取る"""
    try:
        return json.loads(sys.stdin.read())
    except (json.JSONDecodeError, EOFError):
        return None


def load_sessions(file_path):
    """セッションファイルを読み込む。なければ空の構造を返す"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict) and "sessions" in data:
                return data
    except (FileNotFoundError, json.JSONDecodeError, IOError):
        pass
    return {"sessions": []}


def save_sessions(file_path, data):
    """セッションファイルを書き出す"""
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def main():
    try:
        data = read_input()
        if not data:
            sys.exit(0)

        session_id = data.get("session_id")
        cwd = data.get("cwd")

        if not session_id or not cwd:
            sys.exit(0)

        file_path = os.path.join(cwd, SESSIONS_FILE)
        is_new_file = not os.path.exists(file_path)

        sessions_data = load_sessions(file_path)
        sessions = sessions_data["sessions"]

        # 最新エントリと同じ session_id なら重複スキップ
        if sessions and sessions[-1].get("session_id") == session_id:
            sys.exit(0)

        # 新エントリを追加
        entry = {
            "session_id": session_id,
            "started_at": datetime.now(timezone.utc).astimezone().isoformat(),
            "project_path": cwd,
        }
        sessions.append(entry)

        # 履歴上限でトリム
        if len(sessions) > MAX_HISTORY:
            sessions = sessions[-MAX_HISTORY:]
            sessions_data["sessions"] = sessions

        save_sessions(file_path, sessions_data)

        # 初回作成時は .gitignore への追加を案内
        if is_new_file:
            print(
                f"[session-saver] {SESSIONS_FILE} を作成しました。"
                f" .gitignore への追加を推奨します: echo '{SESSIONS_FILE}' >> .gitignore",
                file=sys.stderr,
            )

    except Exception:
        # 何があっても絶対にブロックしない
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
