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
import time
from datetime import datetime, timezone

MAX_HISTORY = 100
SESSIONS_FILE = ".claude-sessions.json"
LOCK_TIMEOUT = 300  # スタールロックと見なす秒数（5分）


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


def update_sessions_with_lock(file_path, session_id, cwd):
    """ロック取得→ロード→更新→書き込みをアトミックに実行。(saved, is_new_file) を返す"""
    lock_path = file_path + ".lock"
    # スタールロック検出 (LOCK_TIMEOUT 秒以上古いロックは削除)
    if os.path.exists(lock_path):
        try:
            if time.time() - os.path.getmtime(lock_path) > LOCK_TIMEOUT:
                os.remove(lock_path)
        except OSError:
            pass
    try:
        lock_fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        return False, False
    try:
        # ロック取得後に is_new_file を判定（TOCTOU防止）
        is_new_file = not os.path.exists(file_path)
        sessions_data = load_sessions(file_path)
        sessions = sessions_data["sessions"]
        if sessions and sessions[-1].get("session_id") == session_id:
            return False, False
        entry = {
            "session_id": session_id,
            "started_at": datetime.now(timezone.utc).astimezone().isoformat(),
            "project_path": cwd,
        }
        sessions.append(entry)
        if len(sessions) > MAX_HISTORY:
            sessions = sessions[-MAX_HISTORY:]
            sessions_data["sessions"] = sessions
        # O_NOFOLLOW でシンボリックリンク経由の書き込みを防止、0o600 で権限制限
        fd = os.open(file_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | os.O_NOFOLLOW, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(sessions_data, f, indent=2, ensure_ascii=False)
            f.write("\n")
        return True, is_new_file
    finally:
        os.close(lock_fd)
        try:
            os.remove(lock_path)
        except OSError:
            pass


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

        saved, is_new_file = update_sessions_with_lock(file_path, session_id, cwd)

        # 初回作成時は .gitignore への追加を案内
        if saved and is_new_file:
            print(
                f"[session-saver] {SESSIONS_FILE} を作成しました。"
                f" .gitignore への追加を推奨します: echo '{SESSIONS_FILE}' >> .gitignore",
                file=sys.stderr,
            )

    except Exception as e:
        # 何があっても絶対にブロックしない
        print(f"[session-saver] 予期しないエラーが発生しました: {e}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
