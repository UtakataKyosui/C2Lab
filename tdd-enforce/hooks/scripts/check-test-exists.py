#!/usr/bin/env python3
"""
PreToolUse hook: TDD 準拠チェック（Blocking）

Edit/Write ツール使用前に実行され、実装コードに対応するテストが
存在するかをチェックする。テストがない場合はブロックする。

- 実装コードの変更時のみチェック（テストファイル・設定ファイルはスキップ）
- テストファイルが存在しない場合は exit 1 でブロック
- 外部依存なし（stdlib のみ）
"""

import json
import os
import re
import sys


def read_input():
    """stdin から PostToolUse の JSON データを読み取る"""
    try:
        data = json.loads(sys.stdin.read())
        return data
    except (json.JSONDecodeError, EOFError, OSError, UnicodeDecodeError):
        return None


def extract_file_path(data):
    """ツール実行データからファイルパスを抽出する"""
    if not data:
        return None
    tool_input = data.get("tool_input", {})
    if "file_path" in tool_input:
        return tool_input["file_path"]
    return None


def is_excluded_file(file_path):
    """テスト不要なファイルかどうか判定する"""
    basename = os.path.basename(file_path)
    dirname = os.path.dirname(file_path)

    # 設定ファイル
    config_patterns = [
        r".*\.config\.",
        r".*\.json$",
        r".*\.yaml$",
        r".*\.yml$",
        r".*\.toml$",
        r".*\.lock$",
        r".*\.env.*",
        r"Cargo\.toml$",
        r"Cargo\.lock$",
        r"package\.json$",
        r"package-lock\.json$",
        r"tsconfig.*\.json$",
        r"go\.mod$",
        r"go\.sum$",
        r"Makefile$",
        r"Dockerfile.*",
        r"docker-compose.*",
        r"\.gitignore$",
        r"\.eslintrc.*",
        r"\.prettierrc.*",
    ]

    for pattern in config_patterns:
        if re.match(pattern, basename):
            return True

    # ドキュメント
    if basename.lower().endswith((".md", ".txt", ".rst")):
        return True
    if basename.upper() in ("LICENSE", "LICENCE", "CHANGELOG", "AUTHORS"):
        return True

    # 型定義のみ
    if basename.endswith((".d.ts", ".types.ts")):
        return True

    # バレルファイル
    if basename in ("index.ts", "index.tsx", "index.js", "index.jsx"):
        return True

    # __init__.py
    if basename == "__init__.py":
        return True

    # CI/CD
    if "/.github/" in file_path or "/.circleci/" in file_path:
        return True

    # main エントリーポイント（テスト緩和対象）
    if basename in ("main.rs", "main.go", "main.py"):
        return True

    # mod.rs (Rust モジュール宣言)
    if basename == "mod.rs":
        return True

    # CSS / HTML / 画像等
    non_code_ext = (
        ".css", ".scss", ".sass", ".less",
        ".html", ".htm", ".svg",
        ".png", ".jpg", ".jpeg", ".gif", ".ico",
        ".woff", ".woff2", ".ttf", ".eot",
    )
    if any(basename.endswith(ext) for ext in non_code_ext):
        return True

    return False


def is_test_file(file_path):
    """テストファイルかどうか判定する"""
    basename = os.path.basename(file_path)

    # TypeScript / JavaScript
    if re.match(r".*\.(test|spec)\.(ts|tsx|js|jsx)$", basename):
        return True

    # Python
    if re.match(r"^test_.*\.py$", basename) or re.match(r".*_test\.py$", basename):
        return True
    if basename == "conftest.py":
        return True

    # Go
    if basename.endswith("_test.go"):
        return True

    # Java
    if re.match(r".*Test\.java$", basename) or re.match(r".*Tests\.java$", basename):
        return True

    # __tests__ ディレクトリ内
    path_parts = file_path.replace("\\", "/").split("/")
    if "__tests__" in path_parts or "tests" in path_parts:
        return True

    return False


def is_source_code(file_path):
    """ソースコードファイルかどうか判定する"""
    code_extensions = (
        ".rs", ".ts", ".tsx", ".js", ".jsx",
        ".py", ".go", ".java", ".cs",
        ".rb", ".ex", ".exs", ".swift",
    )
    return any(file_path.endswith(ext) for ext in code_extensions)


def find_test_file(file_path):
    """対応するテストファイルを探す"""
    dirname = os.path.dirname(file_path)
    basename = os.path.basename(file_path)
    name_without_ext = os.path.splitext(basename)[0]
    ext = os.path.splitext(basename)[1]

    # Rust: 同一ファイル内の #[cfg(test)] をチェック
    if ext == ".rs":
        return check_rust_inline_test(file_path)

    # TypeScript / JavaScript
    if ext in (".ts", ".tsx", ".js", ".jsx"):
        test_patterns = [
            os.path.join(dirname, f"{name_without_ext}.test{ext}"),
            os.path.join(dirname, f"{name_without_ext}.spec{ext}"),
            os.path.join(dirname, "__tests__", f"{name_without_ext}{ext}"),
            os.path.join(dirname, "__tests__", f"{name_without_ext}.test{ext}"),
        ]
        # .tsx → .test.ts, .ts → .test.tsx のクロスチェック
        if ext == ".tsx":
            test_patterns.append(os.path.join(dirname, f"{name_without_ext}.test.ts"))
        elif ext == ".ts":
            test_patterns.append(os.path.join(dirname, f"{name_without_ext}.test.tsx"))
        return any(os.path.exists(p) for p in test_patterns)

    # Python
    if ext == ".py":
        test_patterns = [
            os.path.join(dirname, f"test_{basename}"),
            os.path.join(dirname, f"{name_without_ext}_test.py"),
            os.path.join(dirname, "tests", f"test_{basename}"),
            os.path.join(os.path.dirname(dirname), "tests", f"test_{basename}"),
        ]
        return any(os.path.exists(p) for p in test_patterns)

    # Go
    if ext == ".go":
        test_file = os.path.join(dirname, f"{name_without_ext}_test.go")
        return os.path.exists(test_file)

    # Java
    if ext == ".java":
        test_patterns = [
            os.path.join(dirname, f"{name_without_ext}Test.java"),
            os.path.join(dirname, f"{name_without_ext}Tests.java"),
        ]
        # src/main → src/test 変換
        if "/src/main/" in file_path:
            test_dir = file_path.replace("/src/main/", "/src/test/")
            test_dir = os.path.dirname(test_dir)
            test_patterns.extend([
                os.path.join(test_dir, f"{name_without_ext}Test.java"),
                os.path.join(test_dir, f"{name_without_ext}Tests.java"),
            ])
        return any(os.path.exists(p) for p in test_patterns)

    return True  # 未対応言語はパス


def check_rust_inline_test(file_path):
    """Rust ファイル内にインラインテストがあるかチェック"""
    if not os.path.isfile(file_path):
        return True  # ファイルが存在しない/通常ファイルでない場合はスキップ
    name_without_ext = os.path.splitext(os.path.basename(file_path))[0]
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        # #[cfg(test)] または #[test] の存在チェック
        if "#[cfg(test)]" in content or "#[test]" in content:
            return True
        # tests/ ディレクトリの統合テストをチェック
        project_root = find_project_root(file_path)
        if project_root:
            tests_dir = os.path.join(project_root, "tests")
            if os.path.isdir(tests_dir):
                # tests/ にソースファイルに対応するファイルがあるかチェック
                for f in os.listdir(tests_dir):
                    if f.endswith(".rs") and os.path.splitext(f)[0] == name_without_ext:
                        return True
        return False
    except OSError:
        return True  # 読めない場合はパス


def find_project_root(file_path):
    """プロジェクトルートを探す"""
    current = os.path.dirname(file_path)
    markers = ["Cargo.toml", "package.json", "go.mod", "pyproject.toml", ".git"]
    for _ in range(10):  # 最大10階層
        for marker in markers:
            if os.path.exists(os.path.join(current, marker)):
                return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return None


def main():
    data = read_input()
    file_path = extract_file_path(data)

    if not file_path:
        sys.exit(0)

    # ソースコードでなければスキップ
    if not is_source_code(file_path):
        sys.exit(0)

    # 除外ファイルはスキップ
    if is_excluded_file(file_path):
        sys.exit(0)

    # テストファイル自体の編集はスキップ
    if is_test_file(file_path):
        sys.exit(0)

    # テストファイルの存在チェック
    has_test = find_test_file(file_path)

    if not has_test:
        basename = os.path.basename(file_path)
        print(
            f"[TDD] ⛔ テストが見つかりません: {basename}\n"
            f"[TDD] TDD では実装の前にテストを書く必要があります。\n"
            f"[TDD] まず対応するテストファイルを作成してください。",
            file=sys.stderr,
        )
        sys.exit(1)  # ブロック

    sys.exit(0)


if __name__ == "__main__":
    main()
