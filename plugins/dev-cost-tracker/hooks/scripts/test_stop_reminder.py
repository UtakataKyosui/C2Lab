"""stop_reminder.py のユニットテスト"""

import json
import os
import sys
from io import StringIO
from unittest.mock import patch

import pytest

# テスト対象のモジュールをインポートできるようにパスを追加
sys.path.insert(0, os.path.dirname(__file__))

from stop_reminder import is_session_tracked, main, read_input

COSTS_FILE = ".dev-costs.json"


class TestReadInput:
    """read_input() のテスト"""

    def test_valid_json(self):
        """正常な JSON を読み込める"""
        data = {"session_id": "abc-123", "cwd": "/tmp"}
        with patch("sys.stdin", StringIO(json.dumps(data))):
            result = read_input()
        assert result == data

    def test_invalid_json(self):
        """不正な JSON で None を返す"""
        with patch("sys.stdin", StringIO("not json")):
            result = read_input()
        assert result is None

    def test_empty_input(self):
        """空入力で None を返す"""
        with patch("sys.stdin", StringIO("")):
            result = read_input()
        assert result is None


class TestIsSessionTracked:
    """is_session_tracked() のテスト"""

    def test_found(self, tmp_path):
        """セッションが記録済みなら True"""
        costs_file = tmp_path / COSTS_FILE
        costs_data = {
            "version": "1.0.0",
            "records": [
                {"session_id": "abc-123", "feature_name": "test"},
                {"session_id": "def-456", "feature_name": "test2"},
            ],
        }
        costs_file.write_text(json.dumps(costs_data))
        assert is_session_tracked(str(tmp_path), "abc-123") is True

    def test_not_found(self, tmp_path):
        """未記録なら False"""
        costs_file = tmp_path / COSTS_FILE
        costs_data = {
            "version": "1.0.0",
            "records": [
                {"session_id": "abc-123", "feature_name": "test"},
            ],
        }
        costs_file.write_text(json.dumps(costs_data))
        assert is_session_tracked(str(tmp_path), "xyz-999") is False

    def test_no_file(self, tmp_path):
        """ファイルなしで False"""
        assert is_session_tracked(str(tmp_path), "abc-123") is False

    def test_corrupt_json(self, tmp_path):
        """不正 JSON で False"""
        costs_file = tmp_path / COSTS_FILE
        costs_file.write_text("not valid json")
        assert is_session_tracked(str(tmp_path), "abc-123") is False

    def test_empty_records(self, tmp_path):
        """空の records 配列で False"""
        costs_file = tmp_path / COSTS_FILE
        costs_data = {"version": "1.0.0", "records": []}
        costs_file.write_text(json.dumps(costs_data))
        assert is_session_tracked(str(tmp_path), "abc-123") is False


class TestMain:
    """main() のテスト"""

    def test_untracked_prints_reminder(self, tmp_path):
        """未記録時にリマインダーを stderr に出力"""
        data = {"session_id": "abc-123", "cwd": str(tmp_path)}
        with (
            patch("sys.stdin", StringIO(json.dumps(data))),
            patch("sys.stderr", new_callable=StringIO) as mock_stderr,
            pytest.raises(SystemExit) as exc_info,
        ):
            main()
        assert exc_info.value.code == 0
        output = mock_stderr.getvalue()
        assert "record-cost" in output
        assert "dev-cost-tracker" in output.lower() or "コスト" in output

    def test_tracked_no_output(self, tmp_path):
        """記録済み時は出力なし"""
        costs_file = tmp_path / COSTS_FILE
        costs_data = {
            "version": "1.0.0",
            "records": [{"session_id": "abc-123", "feature_name": "test"}],
        }
        costs_file.write_text(json.dumps(costs_data))
        data = {"session_id": "abc-123", "cwd": str(tmp_path)}
        with (
            patch("sys.stdin", StringIO(json.dumps(data))),
            patch("sys.stderr", new_callable=StringIO) as mock_stderr,
            pytest.raises(SystemExit) as exc_info,
        ):
            main()
        assert exc_info.value.code == 0
        assert mock_stderr.getvalue() == ""

    def test_invalid_input_no_crash(self):
        """不正な入力でもクラッシュしない"""
        with (
            patch("sys.stdin", StringIO("bad")),
            patch("sys.stderr", new_callable=StringIO),
        ):
            # exit(0) するので SystemExit をキャッチ
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_missing_session_id(self):
        """session_id がない場合も exit 0"""
        data = {"cwd": "/tmp"}
        with (
            patch("sys.stdin", StringIO(json.dumps(data))),
            patch("sys.stderr", new_callable=StringIO),
        ):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0
